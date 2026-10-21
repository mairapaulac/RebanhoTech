from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import AnimalForm


def animal_cadastro(request):
    if request.method == 'POST':
        form = AnimalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Animal cadastrado com sucesso!')
            return redirect('animal_cadastro')
        else:
            messages.error(request, 'Erro ao cadastrar o animal. Verifique os campos abaixo.')
    else:
        form = AnimalForm()

    return render(request, 'rebanho/animal_form.html', {'form': form})
