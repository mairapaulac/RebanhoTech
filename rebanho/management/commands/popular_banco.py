import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from rebanho.models import Propriedade, Animal, Pesagem, Vacinacao, Reproducao
from core.models import Movimentacao, Anuncio, Negociacao, Notificacao

class Command(BaseCommand):
    help = 'Popula a base de dados com registos ficticios para testes'

    def handle(self, *args, **kwargs):
        fake = Faker('pt_BR')
        
        self.stdout.write('A criar utilizador administrador...')
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@rebanhotech.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        self.stdout.write('A criar utilizadores adicionais...')
        usuarios = [admin_user]
        for _ in range(5):
            u = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='senha123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            usuarios.append(u)

        self.stdout.write('A criar propriedades...')
        propriedades = []
        estados = ['PE', 'BA', 'CE', 'PB', 'RN']
        for _ in range(10):
            prop = Propriedade.objects.create(
                criador=random.choice(usuarios),
                nome=f"Fazenda {fake.company()}",
                area_hectares=round(random.uniform(20.0, 500.0), 2),
                cidade=fake.city(),
                estado=random.choice(estados)
            )
            propriedades.append(prop)

        self.stdout.write('A criar animais e registos de saude...')
        racas = ['Santa Inês', 'Dorper', 'White Dorper', 'Morada Nova', 'Somalis']
        vacinas = ['Aftosa', 'Clostridiose', 'Raiva', 'Linfadenite Caseosa']
        animais = []

        for i in range(150):
            sexo = random.choice(['M', 'F'])
            animal = Animal.objects.create(
                brinco=f"BR{1000 + i}",
                raca=random.choice(racas),
                sexo=sexo,
                data_nascimento=fake.date_between(start_date='-4y', end_date='-6m'),
                propriedade=random.choice(propriedades)
            )
            animais.append(animal)

            # Criar pesagens
            for j in range(random.randint(2, 4)):
                Pesagem.objects.create(
                    animal=animal,
                    peso_kg=round(random.uniform(25.0, 85.0), 2),
                    data_pesagem=date.today() - timedelta(days=j*60)
                )

            # Criar vacinaçoes
            Vacinacao.objects.create(
                animal=animal,
                vacina=random.choice(vacinas),
                data_aplicacao=fake.date_between(start_date='-1y', end_date='today'),
                proxima_dose=date.today() + timedelta(days=180)
            )

            # Criar reproduçao para femeas
            if sexo == 'F' and random.choice([True, False]):
                Reproducao.objects.create(
                    matriz=animal,
                    data_cobertura=fake.date_between(start_date='-1y', end_date='-5m'),
                    data_parto=fake.date_between(start_date='-4m', end_date='today'),
                    qtd_crias=random.choice([1, 2]),
                    observacao="Parto sem complicações"
                )

        self.stdout.write('A criar movimentaçoes, anuncios e notificaçoes...')
        for _ in range(20):
            a = random.choice(animais)
            p_origem = a.propriedade
            p_destino = random.choice([p for p in propriedades if p != p_origem])
            
            Movimentacao.objects.create(
                animal=a,
                origem=p_origem,
                destino=p_destino,
                data_movimentacao=fake.date_between(start_date='-6m', end_date='today'),
                motivo=random.choice(['Venda de matriz', 'Manejo de pastagem', 'Exposição regional'])
            )

        for _ in range(15):
            anuncio = Anuncio.objects.create(
                vendedor=random.choice(usuarios),
                animal=random.choice(animais),
                titulo=f"Oportunidade - Reproductor/Matriz de Alta Categoria",
                preco=round(random.uniform(800.0, 3500.0), 2),
                descricao="Excelente padrao genetico, vacinaçao em dia e apto para reproduçao.",
                ativo=True
            )

            for _ in range(random.randint(1, 3)):
                Negociacao.objects.create(
                    anuncio=anuncio,
                    comprador=random.choice(usuarios),
                    valor_proposto=anuncio.preco * round(random.uniform(0.85, 1.0), 2),
                    status=random.choice(['EM_ANDAMENTO', 'CONCLUIDA'])
                )

        for u in usuarios:
            Notificacao.objects.create(
                usuario=u,
                titulo="Bem-vindo ao RebanhoTech",
                mensagem="A sua conta foi configurada com sucesso no sistema.",
                lida=True
            )

        self.stdout.write(self.style.SUCCESS('Base de dados populada com sucesso!'))