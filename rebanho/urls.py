from django.urls import path
from . import views

urlpatterns = [
    # Propriedades
    path('propriedades/', views.propriedade_list, name='propriedade_list'),
    path('propriedades/cadastrar/', views.propriedade_create, name='propriedade_create'),
    path('propriedades/<int:pk>/editar/', views.propriedade_update, name='propriedade_update'),
    path('propriedades/<int:pk>/excluir/', views.propriedade_delete, name='propriedade_delete'),

    # Animais
    path('', views.animal_list, name='animal_list'),
    path('animais/', views.animal_list, name='animal_list_alias'),
    path('cadastrar/', views.animal_cadastro, name='animal_cadastro'),
    path('animais/cadastrar/', views.animal_cadastro, name='animal_cadastro_alias'),
    path('animais/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('animais/<int:pk>/editar/', views.animal_update, name='animal_update'),
    path('animais/<int:pk>/excluir/', views.animal_delete, name='animal_delete'),

    # Pesagens
    path('pesagens/', views.pesagem_list, name='pesagem_list'),
    path('pesagens/cadastrar/', views.pesagem_create, name='pesagem_create'),
    path('pesagens/<int:pk>/excluir/', views.pesagem_delete, name='pesagem_delete'),

    # Vacinações
    path('vacinacoes/', views.vacinacao_list, name='vacinacao_list'),
    path('vacinacoes/cadastrar/', views.vacinacao_create, name='vacinacao_create'),
    path('vacinacoes/<int:pk>/excluir/', views.vacinacao_delete, name='vacinacao_delete'),

    # Reproduções
    path('reproducoes/', views.reproducao_list, name='reproducao_list'),
    path('reproducoes/cadastrar/', views.reproducao_create, name='reproducao_create'),
    path('reproducoes/<int:pk>/excluir/', views.reproducao_delete, name='reproducao_delete'),
]
