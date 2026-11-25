from datetime import date, timedelta
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .forms import AnimalForm, PesagemForm, PropriedadeForm, ReproducaoForm, VacinacaoForm
from .models import Animal, Pesagem, Propriedade, Reproducao, Vacinacao


class RebanhoModelsAndFormsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='criador1', password='password123')
        self.client = Client()
        self.client.login(username='criador1', password='password123')

        self.propriedade1 = Propriedade.objects.create(
            criador=self.user,
            nome='Fazenda Boa Esperança',
            area_hectares=150.0,
            cidade='Petrolina',
            estado='PE'
        )
        self.propriedade2 = Propriedade.objects.create(
            criador=self.user,
            nome='Sítio Recanto Feliz',
            area_hectares=45.0,
            cidade='Juazeiro',
            estado='BA'
        )

        self.animal1 = Animal.objects.create(
            brinco='BR001',
            raca='Santa Inês',
            sexo='M',
            data_nascimento=date.today() - timedelta(days=500),
            propriedade=self.propriedade1
        )
        self.matriz = Animal.objects.create(
            brinco='BR002',
            raca='Santa Inês',
            sexo='F',
            data_nascimento=date.today() - timedelta(days=600),
            propriedade=self.propriedade1
        )

    def test_propriedade_form_valido(self):
        form = PropriedadeForm(data={
            'nome': 'Fazenda Modelo',
            'area_hectares': 80.5,
            'cidade': 'Lagoa Grande',
            'estado': 'PE'
        })
        self.assertTrue(form.is_valid())

    def test_propriedade_area_invalida(self):
        form = PropriedadeForm(data={
            'nome': 'Fazenda Modelo',
            'area_hectares': -10.0,
            'cidade': 'Lagoa Grande',
            'estado': 'PE'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('area_hectares', form.errors)

    def test_animal_data_nascimento_futura(self):
        form = AnimalForm(data={
            'brinco': 'BR999',
            'raca': 'Dorper',
            'sexo': 'M',
            'data_nascimento': date.today() + timedelta(days=5),
            'propriedade': self.propriedade1.id,
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('data_nascimento', form.errors)

    def test_animal_brinco_duplicado(self):
        form = AnimalForm(data={
            'brinco': 'BR001',
            'raca': 'Dorper',
            'sexo': 'M',
            'data_nascimento': date.today() - timedelta(days=100),
            'propriedade': self.propriedade1.id,
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('brinco', form.errors)

    def test_pesagem_valida_e_invalida(self):
        form_valido = PesagemForm(data={
            'animal': self.animal1.id,
            'peso_kg': 55.4,
            'data_pesagem': date.today(),
        }, user=self.user)
        self.assertTrue(form_valido.is_valid())

        form_peso_negativo = PesagemForm(data={
            'animal': self.animal1.id,
            'peso_kg': -5.0,
            'data_pesagem': date.today(),
        }, user=self.user)
        self.assertFalse(form_peso_negativo.is_valid())
        self.assertIn('peso_kg', form_peso_negativo.errors)

    def test_vacinacao_datas(self):
        form_valido = VacinacaoForm(data={
            'animal': self.animal1.id,
            'vacina': 'Clostridiose',
            'data_aplicacao': date.today() - timedelta(days=10),
            'proxima_dose': date.today() + timedelta(days=180),
        }, user=self.user)
        self.assertTrue(form_valido.is_valid())

        form_data_incoerente = VacinacaoForm(data={
            'animal': self.animal1.id,
            'vacina': 'Clostridiose',
            'data_aplicacao': date.today(),
            'proxima_dose': date.today() - timedelta(days=10),
        }, user=self.user)
        self.assertFalse(form_data_incoerente.is_valid())
        self.assertIn('proxima_dose', form_data_incoerente.errors)

    def test_reproducao_matriz_femea(self):
        form_valido = ReproducaoForm(data={
            'matriz': self.matriz.id,
            'data_cobertura': date.today() - timedelta(days=150),
            'data_parto': date.today() - timedelta(days=5),
            'qtd_crias': 2,
            'observacao': 'Gêmeos saudáveis'
        }, user=self.user)
        self.assertTrue(form_valido.is_valid())

    def test_animal_views_acesso(self):
        resp_lista = self.client.get(reverse('animal_list'))
        self.assertEqual(resp_lista.status_code, 200)
        self.assertContains(resp_lista, 'BR001')

        resp_detalhe = self.client.get(reverse('animal_detail', args=[self.animal1.pk]))
        self.assertEqual(resp_detalhe.status_code, 200)
        self.assertContains(resp_detalhe, 'BR001')
