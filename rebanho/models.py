from django.db import models
from django.contrib.auth.models import User

class Propriedade(models.Model):
    criador = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criador")
    nome = models.CharField(max_length=100, verbose_name="Nome da Propriedade")
    area_hectares = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Área (ha)")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="UF")

    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"

    def __str__(self):
        return f"{self.nome} - {self.cidade}/{self.estado}"


class Animal(models.Model):
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]

    brinco = models.CharField(max_length=30, unique=True, verbose_name="Número do Brinco")
    raca = models.CharField(max_length=50, verbose_name="Raça")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, verbose_name="Propriedade")
    
    # Auto-relacionamento para arvore genealogica
    pai = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='filhos_pai', verbose_name="Pai")
    mae = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='filhos_mae', verbose_name="Mãe")

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"

    def __str__(self):
        return f"Brinco {self.brinco} ({self.raca})"


class Pesagem(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='pesagens', verbose_name="Animal")
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Peso (kg)")
    data_pesagem = models.DateField(verbose_name="Data da Pesagem")

    class Meta:
        verbose_name = "Pesagem"
        verbose_name_plural = "Pesagens"

    def __str__(self):
        return f"{self.animal.brinco} - {self.peso_kg} kg"


class Vacinacao(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='vacinas', verbose_name="Animal")
    vacina = models.CharField(max_length=100, verbose_name="Nome da Vacina")
    data_aplicacao = models.DateField(verbose_name="Data de Aplicação")
    proxima_dose = models.DateField(null=True, blank=True, verbose_name="Próxima Dose")

    class Meta:
        verbose_name = "Vacinação"
        verbose_name_plural = "Vacinações"

    def __str__(self):
        return f"{self.animal.brinco} - {self.vacina}"


class Reproducao(models.Model):
    matriz = models.ForeignKey(Animal, limit_choices_to={'sexo': 'F'}, on_delete=models.CASCADE, verbose_name="Matriz (Fêmea)")
    data_cobertura = models.DateField(verbose_name="Data da Cobertura/IA")
    data_parto = models.DateField(null=True, blank=True, verbose_name="Data do Parto")
    qtd_crias = models.PositiveIntegerField(default=1, verbose_name="Quantidade de Crias")
    observacao = models.TextField(blank=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Reprodução"
        verbose_name_plural = "Registros de Reprodução"

    def __str__(self):
        return f"Matriz {self.matriz.brinco} - Cobertura: {self.data_cobertura}"