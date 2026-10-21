from datetime import date

from django import forms

from .models import Animal


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['brinco', 'raca', 'sexo', 'data_nascimento', 'propriedade', 'pai', 'mae']

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data['data_nascimento']
        if data_nascimento > date.today():
            raise forms.ValidationError('A data de nascimento não pode ser no futuro.')
        return data_nascimento
