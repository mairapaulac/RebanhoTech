from datetime import date, timedelta
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .forms import MovimentacaoForm
from .models import Anuncio, Movimentacao, Negociacao, Notificacao
from rebanho.models import Animal, Propriedade


class CoreAppTests(TestCase):
    def setUp(self):
        self.vendedor = User.objects.create_user(username='vendedor1', email='vendedor@teste.com', password='senha123')
        self.comprador = User.objects.create_user(username='comprador1', email='comprador@teste.com', password='senha123')

        self.propriedade_a = Propriedade.objects.create(
            criador=self.vendedor,
            nome='Fazenda Sol Nascente',
            area_hectares=100.0,
            cidade='Petrolina',
            estado='PE'
        )
        self.propriedade_b = Propriedade.objects.create(
            criador=self.vendedor,
            nome='Pasto Verde',
            area_hectares=50.0,
            cidade='Santa Maria da Boa Vista',
            estado='PE'
        )

        self.animal = Animal.objects.create(
            brinco='BR777',
            raca='Santa Inês',
            sexo='M',
            data_nascimento=date.today() - timedelta(days=400),
            propriedade=self.propriedade_a
        )

        self.anuncio = Anuncio.objects.create(
            vendedor=self.vendedor,
            animal=self.animal,
            titulo='Reprodutor PO Santa Inês',
            preco=2500.00,
            descricao='Excelente animal, vacinado e vermifugado.',
            ativo=True
        )

    def test_registro_usuario(self):
        client = Client()
        response = client.post(reverse('register'), {
            'username': 'novocriador',
            'first_name': 'Carlos',
            'last_name': 'Silva',
            'email': 'carlos@rebanho.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='novocriador').exists())

    def test_movimentacao_atualiza_propriedade_do_animal(self):
        client = Client()
        client.login(username='vendedor1', password='senha123')

        # Animal está na propriedade A
        self.assertEqual(self.animal.propriedade, self.propriedade_a)

        response = client.post(reverse('movimentacao_create'), {
            'animal': self.animal.id,
            'origem': self.propriedade_a.id,
            'destino': self.propriedade_b.id,
            'data_movimentacao': date.today(),
            'motivo': 'Mudança de pasto para engorda',
        })
        self.assertEqual(response.status_code, 302)

        # Atualiza a instância do banco
        self.animal.refresh_from_db()
        self.assertEqual(self.animal.propriedade, self.propriedade_b)
        self.assertTrue(Movimentacao.objects.filter(animal=self.animal, destino=self.propriedade_b).exists())

    def test_proposta_no_marketplace_cria_notificacao_ao_vendedor(self):
        client = Client()
        client.login(username='comprador1', password='senha123')

        response = client.post(reverse('anuncio_detail', args=[self.anuncio.id]), {
            'valor_proposto': 2200.00
        })
        self.assertEqual(response.status_code, 302)

        # Negociação criada
        proposta = Negociacao.objects.filter(anuncio=self.anuncio, comprador=self.comprador).first()
        self.assertIsNotNone(proposta)
        self.assertEqual(float(proposta.valor_proposto), 2200.00)
        self.assertEqual(proposta.status, 'EM_ANDAMENTO')

        # Notificação criada para o vendedor
        notif = Notificacao.objects.filter(usuario=self.vendedor, lida=False).first()
        self.assertIsNotNone(notif)
        self.assertIn('Nova Proposta de Compra', notif.titulo)

    def test_aceitar_proposta_finaliza_anuncio_e_notifica_comprador(self):
        # Comprador cria proposta
        proposta = Negociacao.objects.create(
            anuncio=self.anuncio,
            comprador=self.comprador,
            valor_proposto=2300.00,
            status='EM_ANDAMENTO'
        )

        client = Client()
        client.login(username='vendedor1', password='senha123')

        response = client.post(reverse('aceitar_proposta', args=[proposta.id]))
        self.assertEqual(response.status_code, 302)

        proposta.refresh_from_db()
        self.anuncio.refresh_from_db()

        self.assertEqual(proposta.status, 'CONCLUIDA')
        self.assertFalse(self.anuncio.ativo)

        # Notificação criada para o comprador
        notif = Notificacao.objects.filter(usuario=self.comprador).first()
        self.assertIsNotNone(notif)
        self.assertIn('Proposta Aceita', notif.titulo)

    def test_api_rest_endpoints(self):
        client = Client()

        # Teste endpoint API Anúncios
        resp_anuncios = client.get(reverse('api_anuncios'))
        self.assertEqual(resp_anuncios.status_code, 200)
        data_anuncios = resp_anuncios.json()
        self.assertIn('anuncios', data_anuncios)
        self.assertGreaterEqual(data_anuncios['total'], 1)

        # Teste endpoint API Animais
        resp_animais = client.get(reverse('api_animais'))
        self.assertEqual(resp_animais.status_code, 200)
        data_animais = resp_animais.json()
        self.assertIn('animais', data_animais)

        # Teste endpoint API Estatísticas
        resp_stats = client.get(reverse('api_estatisticas'))
        self.assertEqual(resp_stats.status_code, 200)
        data_stats = resp_stats.json()
        self.assertIn('total_animais', data_stats)
        self.assertIn('total_propriedades', data_stats)
