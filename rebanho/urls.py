from django.urls import path

from . import views

urlpatterns = [
    path('cadastrar/', views.animal_cadastro, name='animal_cadastro'),
]
