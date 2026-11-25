from datetime import date
from django import forms
from .models import Propriedade, Animal, Pesagem, Vacinacao, Reproducao


class PropriedadeForm(forms.ModelForm):
    class Meta:
        model = Propriedade
        fields = ['nome', 'area_hectares', 'cidade', 'estado']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Fazenda ou Sítio'}),
            'area_hectares': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 120.50', 'step': '0.01'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF (ex: PE, BA)', 'maxlength': '2'}),
        }

    def clean_area_hectares(self):
        area = self.cleaned_data.get('area_hectares')
        if area is not None and area <= 0:
            raise forms.ValidationError('A área da propriedade deve ser maior que zero.')
        return area

    def clean_estado(self):
        estado = self.cleaned_data.get('estado', '').strip().upper()
        if len(estado) != 2:
            raise forms.ValidationError('Informe a sigla do estado com 2 letras (ex: PE, BA).')
        return estado


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['brinco', 'raca', 'sexo', 'data_nascimento', 'propriedade', 'pai', 'mae']
        widgets = {
            'brinco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: BR1001'}),
            'raca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Santa Inês, Dorper, Nelore'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'propriedade': forms.Select(attrs={'class': 'form-select'}),
            'pai': forms.Select(attrs={'class': 'form-select'}),
            'mae': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtra apenas propriedades do usuário logado (a menos que seja superusuário)
            if not user.is_superuser:
                self.fields['propriedade'].queryset = Propriedade.objects.filter(criador=user)
                # Pais e mães devem ser machos e fêmeas respectivamente
                self.fields['pai'].queryset = Animal.objects.filter(sexo='M', propriedade__criador=user)
                self.fields['mae'].queryset = Animal.objects.filter(sexo='F', propriedade__criador=user)
            else:
                self.fields['pai'].queryset = Animal.objects.filter(sexo='M')
                self.fields['mae'].queryset = Animal.objects.filter(sexo='F')

        # Se for edição, remove o próprio animal das opções de pai e mãe
        if self.instance and self.instance.pk:
            self.fields['pai'].queryset = self.fields['pai'].queryset.exclude(pk=self.instance.pk)
            self.fields['mae'].queryset = self.fields['mae'].queryset.exclude(pk=self.instance.pk)

    def clean_brinco(self):
        brinco = self.cleaned_data.get('brinco', '').strip().upper()
        # Verificar duplicidade respeitando a própria instância
        qs = Animal.objects.filter(brinco__iexact=brinco)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'Já existe um animal cadastrado com o brinco "{brinco}".')
        return brinco

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if data_nascimento and data_nascimento > date.today():
            raise forms.ValidationError('A data de nascimento não pode ser no futuro.')
        return data_nascimento

    def clean(self):
        cleaned_data = super().clean()
        pai = cleaned_data.get('pai')
        mae = cleaned_data.get('mae')
        data_nascimento = cleaned_data.get('data_nascimento')

        if pai and pai.sexo != 'M':
            self.add_error('pai', 'O pai selecionado deve ser do sexo Macho.')
        if mae and mae.sexo != 'F':
            self.add_error('mae', 'A mãe selecionada deve ser do sexo Fêmea.')

        if pai and data_nascimento and pai.data_nascimento and pai.data_nascimento >= data_nascimento:
            self.add_error('pai', 'A data de nascimento do pai deve ser anterior à do filho.')

        if mae and data_nascimento and mae.data_nascimento and mae.data_nascimento >= data_nascimento:
            self.add_error('mae', 'A data de nascimento da mãe deve ser anterior à do filho.')

        return cleaned_data


class PesagemForm(forms.ModelForm):
    class Meta:
        model = Pesagem
        fields = ['animal', 'peso_kg', 'data_pesagem']
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-select'}),
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 45.50', 'step': '0.01'}),
            'data_pesagem': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        animal = kwargs.pop('animal', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields['animal'].queryset = Animal.objects.filter(propriedade__criador=user)
        if animal:
            self.fields['animal'].initial = animal
            self.fields['animal'].widget = forms.HiddenInput()

    def clean_peso_kg(self):
        peso = self.cleaned_data.get('peso_kg')
        if peso is not None and peso <= 0:
            raise forms.ValidationError('O peso deve ser maior que zero.')
        return peso

    def clean_data_pesagem(self):
        data_pesagem = self.cleaned_data.get('data_pesagem')
        if data_pesagem and data_pesagem > date.today():
            raise forms.ValidationError('A data da pesagem não pode ser no futuro.')
        return data_pesagem

    def clean(self):
        cleaned_data = super().clean()
        animal = cleaned_data.get('animal')
        data_pesagem = cleaned_data.get('data_pesagem')
        if animal and data_pesagem and animal.data_nascimento and data_pesagem < animal.data_nascimento:
            self.add_error('data_pesagem', 'A pesagem não pode ocorrer antes da data de nascimento do animal.')
        return cleaned_data


class VacinacaoForm(forms.ModelForm):
    class Meta:
        model = Vacinacao
        fields = ['animal', 'vacina', 'data_aplicacao', 'proxima_dose']
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-select'}),
            'vacina': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Clostridiose, Raiva, Aftosa'}),
            'data_aplicacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proxima_dose': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        animal = kwargs.pop('animal', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields['animal'].queryset = Animal.objects.filter(propriedade__criador=user)
        if animal:
            self.fields['animal'].initial = animal
            self.fields['animal'].widget = forms.HiddenInput()

    def clean_data_aplicacao(self):
        data_aplicacao = self.cleaned_data.get('data_aplicacao')
        if data_aplicacao and data_aplicacao > date.today():
            raise forms.ValidationError('A data de aplicação não pode ser no futuro.')
        return data_aplicacao

    def clean(self):
        cleaned_data = super().clean()
        animal = cleaned_data.get('animal')
        data_aplicacao = cleaned_data.get('data_aplicacao')
        proxima_dose = cleaned_data.get('proxima_dose')

        if animal and data_aplicacao and animal.data_nascimento and data_aplicacao < animal.data_nascimento:
            self.add_error('data_aplicacao', 'A vacinação não pode ocorrer antes do nascimento do animal.')

        if data_aplicacao and proxima_dose and proxima_dose < data_aplicacao:
            self.add_error('proxima_dose', 'A data da próxima dose deve ser posterior à data de aplicação.')
        return cleaned_data


class ReproducaoForm(forms.ModelForm):
    class Meta:
        model = Reproducao
        fields = ['matriz', 'data_cobertura', 'data_parto', 'qtd_crias', 'observacao']
        widgets = {
            'matriz': forms.Select(attrs={'class': 'form-select'}),
            'data_cobertura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_parto': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'qtd_crias': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações do parto, intercorrências, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        matriz = kwargs.pop('matriz', None)
        super().__init__(*args, **kwargs)
        qs = Animal.objects.filter(sexo='F')
        if user and not user.is_superuser:
            qs = qs.filter(propriedade__criador=user)
        self.fields['matriz'].queryset = qs
        if matriz:
            self.fields['matriz'].initial = matriz
            self.fields['matriz'].widget = forms.HiddenInput()

    def clean_qtd_crias(self):
        qtd = self.cleaned_data.get('qtd_crias')
        if qtd is not None and qtd < 1:
            raise forms.ValidationError('A quantidade de crias deve ser pelo menos 1.')
        return qtd

    def clean_data_cobertura(self):
        data_cobertura = self.cleaned_data.get('data_cobertura')
        if data_cobertura and data_cobertura > date.today():
            raise forms.ValidationError('A data de cobertura não pode ser no futuro.')
        return data_cobertura

    def clean(self):
        cleaned_data = super().clean()
        matriz = cleaned_data.get('matriz')
        data_cobertura = cleaned_data.get('data_cobertura')
        data_parto = cleaned_data.get('data_parto')

        if matriz and matriz.sexo != 'F':
            self.add_error('matriz', 'Apenas animais fêmeas podem ser registrados como matriz.')

        if matriz and data_cobertura and matriz.data_nascimento and data_cobertura < matriz.data_nascimento:
            self.add_error('data_cobertura', 'A data de cobertura não pode ser anterior ao nascimento da matriz.')

        if data_cobertura and data_parto:
            if data_parto < data_cobertura:
                self.add_error('data_parto', 'A data do parto deve ser posterior à data da cobertura.')
            if data_parto > date.today():
                self.add_error('data_parto', 'A data do parto não pode ser no futuro.')

        return cleaned_data
