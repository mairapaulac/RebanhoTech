from django.db import models
from django.contrib.auth.models import User
from rebanho.models import Animal, Propriedade

class Movimentacao(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name="Animal")
    origem = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='mov_origem', verbose_name="Origem")
    destino = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='mov_destino', verbose_name="Destino")
    data_movimentacao = models.DateField(verbose_name="Data da Movimentação")
    motivo = models.CharField(max_length=150, verbose_name="Motivo")

    class Meta:
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"

    def __str__(self):
        return f"Movimentação do brinco {self.animal.brinco}"


class Anuncio(models.Model):
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Vendedor")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name="Animal")
    titulo = models.CharField(max_length=120, verbose_name="Título do Anúncio")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço (R$)")
    descricao = models.TextField(verbose_name="Descrição")
    data_publicacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Publicação")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Anúncio"
        verbose_name_plural = "Anúncios"

    def __str__(self):
        return self.titulo


class Negociacao(models.Model):
    STATUS_CHOICES = [
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]

    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, verbose_name="Anúncio")
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Comprador")
    valor_proposto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Proposto (R$)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EM_ANDAMENTO', verbose_name="Status")
    data_proposta = models.DateTimeField(auto_now_add=True, verbose_name="Data da Proposta")

    class Meta:
        verbose_name = "Negociação"
        verbose_name_plural = "Negociações"

    def __str__(self):
        return f"Proposta de {self.comprador.username} no anúncio {self.anuncio.id}"


class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    titulo = models.CharField(max_length=100, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    lida = models.BooleanField(default=False, verbose_name="Lida")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"Notificação para {self.usuario.username} - {self.titulo}"