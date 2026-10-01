from django.contrib import admin
from .models import Propriedade, Animal, Pesagem, Vacinacao, Reproducao

class PesagemInline(admin.TabularInline):
    model = Pesagem
    extra = 1

class VacinacaoInline(admin.TabularInline):
    model = Vacinacao
    extra = 1

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criador', 'cidade', 'estado', 'area_hectares')
    search_fields = ('nome', 'cidade', 'criador__username')
    list_filter = ('estado',)

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('brinco', 'raca', 'sexo', 'propriedade', 'data_nascimento')
    search_fields = ('brinco', 'raca', 'propriedade__nome')
    list_filter = ('sexo', 'raca', 'propriedade')
    
    fieldsets = (
        ('Identificação e Localização', {
            'fields': ('brinco', 'propriedade')
        }),
        ('Características do Animal', {
            'fields': ('raca', 'sexo', 'data_nascimento')
        }),
        ('Genealogia', {
            'fields': ('pai', 'mae'),
            'classes': ('collapse',)
        }),
    )
    inlines = [PesagemInline, VacinacaoInline]

@admin.register(Pesagem)
class PesagemAdmin(admin.ModelAdmin):
    list_display = ('animal', 'peso_kg', 'data_pesagem')
    search_fields = ('animal__brinco',)
    list_filter = ('data_pesagem',)

@admin.register(Vacinacao)
class VacinacaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'vacina', 'data_aplicacao', 'proxima_dose')
    search_fields = ('animal__brinco', 'vacina')
    list_filter = ('vacina', 'data_aplicacao')

@admin.register(Reproducao)
class ReproducaoAdmin(admin.ModelAdmin):
    list_display = ('matriz', 'data_cobertura', 'data_parto', 'qtd_crias')
    search_fields = ('matriz__brinco',)
    list_filter = ('data_cobertura', 'data_parto')