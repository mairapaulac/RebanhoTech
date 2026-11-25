from datetime import date
from django import forms
from django.contrib.auth.models import User
from .models import Movimentacao, Anuncio, Negociacao
from rebanho.models import Animal, Propriedade


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Crie uma senha segura'}),
        help_text='Mínimo de 8 caracteres.'
    )
    password_confirm = forms.CharField(
        label='Confirme a Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita a senha'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de usuário único'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu primeiro nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu sobrenome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@email.com'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado em outra conta.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'As senhas informadas não coincidem.')

        if password and len(password) < 8:
            self.add_error('password', 'A senha deve conter pelo menos 8 caracteres.')

        return cleaned_data


class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['animal', 'origem', 'destino', 'data_movimentacao', 'motivo']
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-select'}),
            'origem': forms.Select(attrs={'class': 'form-select'}),
            'destino': forms.Select(attrs={'class': 'form-select'}),
            'data_movimentacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Venda, Manejo de pastagem, Reprodução'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        animal = kwargs.pop('animal', None)
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser:
            # Animal deve pertencer a uma propriedade do usuário
            self.fields['animal'].queryset = Animal.objects.filter(propriedade__criador=user)
            # Origem deve ser propriedade do usuário
            self.fields['origem'].queryset = Propriedade.objects.filter(criador=user)
            # Destino pode ser qualquer propriedade cadastrada no sistema
            self.fields['destino'].queryset = Propriedade.objects.all()

        if animal:
            self.fields['animal'].initial = animal
            self.fields['origem'].initial = animal.propriedade

    def clean_data_movimentacao(self):
        data_mov = self.cleaned_data.get('data_movimentacao')
        if data_mov and data_mov > date.today():
            raise forms.ValidationError('A data da movimentação não pode ser no futuro.')
        return data_mov

    def clean(self):
        cleaned_data = super().clean()
        animal = cleaned_data.get('animal')
        origem = cleaned_data.get('origem')
        destino = cleaned_data.get('destino')

        if origem and destino and origem == destino:
            self.add_error('destino', 'A propriedade de destino deve ser diferente da propriedade de origem.')

        if animal and origem and animal.propriedade != origem:
            self.add_error('origem', f'O animal {animal.brinco} está atualmente na propriedade "{animal.propriedade.nome}". A origem deve corresponder à localização atual.')

        return cleaned_data


class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        fields = ['animal', 'titulo', 'preco', 'descricao', 'ativo']
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Matriz Santa Inês PO com Registro'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1500.00', 'step': '0.01'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva detalhes sobre a linhagem, sanidade, peso e condições de entrega.'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        animal = kwargs.pop('animal', None)
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser:
            self.fields['animal'].queryset = Animal.objects.filter(propriedade__criador=user)

        if animal:
            self.fields['animal'].initial = animal

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco is not None and preco <= 0:
            raise forms.ValidationError('O preço do anúncio deve ser maior que zero.')
        return preco

    def clean(self):
        cleaned_data = super().clean()
        animal = cleaned_data.get('animal')
        ativo = cleaned_data.get('ativo')

        if animal and ativo:
            # Checar se o animal já possui outro anúncio ativo
            qs = Anuncio.objects.filter(animal=animal, ativo=True)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('animal', f'O animal {animal.brinco} já possui um anúncio ativo no Marketplace.')

        return cleaned_data


class NegociacaoForm(forms.ModelForm):
    class Meta:
        model = Negociacao
        fields = ['valor_proposto']
        widgets = {
            'valor_proposto': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Digite o valor da sua proposta em R$',
                'step': '0.01'
            }),
        }

    def clean_valor_proposto(self):
        valor = self.cleaned_data.get('valor_proposto')
        if valor is not None and valor <= 0:
            raise forms.ValidationError('O valor proposto deve ser maior que zero.')
        return valor
