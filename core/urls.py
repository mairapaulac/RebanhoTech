from django.urls import path
from . import views

urlpatterns = [
    # Dashboard / Home
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),

    # Movimentações
    path('movimentacoes/', views.movimentacao_list, name='movimentacao_list'),
    path('movimentacoes/nova/', views.movimentacao_create, name='movimentacao_create'),

    # Marketplace (Anúncios & Negociações)
    path('marketplace/', views.anuncio_list, name='anuncio_list'),
    path('marketplace/anuncio/<int:pk>/', views.anuncio_detail, name='anuncio_detail'),
    path('marketplace/anunciar/', views.anuncio_create, name='anuncio_create'),
    path('marketplace/anuncio/<int:pk>/editar/', views.anuncio_update, name='anuncio_update'),
    path('marketplace/anuncio/<int:pk>/excluir/', views.anuncio_delete, name='anuncio_delete'),
    path('marketplace/meus-anuncios/', views.meus_anuncios, name='meus_anuncios'),
    path('marketplace/minhas-propostas/', views.minhas_propostas, name='minhas_propostas'),
    path('marketplace/proposta/<int:pk>/aceitar/', views.aceitar_proposta, name='aceitar_proposta'),
    path('marketplace/proposta/<int:pk>/recusar/', views.recusar_proposta, name='recusar_proposta'),

    # Notificações
    path('notificacoes/', views.notificacao_list, name='notificacao_list'),
    path('notificacoes/<int:pk>/marcar-lida/', views.notificacao_marcar_lida, name='notificacao_marcar_lida'),
    path('notificacoes/marcar-todas-lidas/', views.notificacoes_marcar_todas_lidas, name='notificacoes_marcar_todas_lidas'),

    # API REST (Requisito Desejável de Integração)
    path('api/anuncios/', views.api_anuncios, name='api_anuncios'),
    path('api/animais/', views.api_animais, name='api_animais'),
    path('api/estatisticas/', views.api_estatisticas, name='api_estatisticas'),
]
