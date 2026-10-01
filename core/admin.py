from django.contrib import admin
from .models import Movimentacao, Anuncio, Negociacao, Notificacao

class NegociacaoInline(admin.TabularInline):
    model = Negociacao
    extra = 1

@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'origem', 'destino', 'data_movimentacao', 'motivo')
    search_fields = ('animal__brinco', 'motivo')
    list_filter = ('data_movimentacao',)

@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'vendedor', 'animal', 'preco', 'ativo', 'data_publicacao')
    search_fields = ('titulo', 'vendedor__username', 'animal__brinco')
    list_filter = ('ativo', 'data_publicacao')
    inlines = [NegociacaoInline]

@admin.register(Negociacao)
class NegociacaoAdmin(admin.ModelAdmin):
    list_display = ('anuncio', 'comprador', 'valor_proposto', 'status', 'data_proposta')
    search_fields = ('anuncio__titulo', 'comprador__username')
    list_filter = ('status', 'data_proposta')

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'titulo', 'lida', 'data_criacao')
    search_fields = ('usuario__username', 'titulo')
    list_filter = ('lida', 'data_criacao')