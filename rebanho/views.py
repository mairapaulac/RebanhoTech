from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnimalForm, PesagemForm, PropriedadeForm, ReproducaoForm, VacinacaoForm
from .models import Animal, Pesagem, Propriedade, Reproducao, Vacinacao


# ==========================================
# PROPRIEDADES
# ==========================================

@login_required
def propriedade_list(request):
    """Lista as propriedades rurais pertencentes ao usuário logado."""
    query = request.GET.get('q', '').strip()
    qs = Propriedade.objects.filter(criador=request.user).annotate(total_animais=Count('animal')).order_by('nome')
    if query:
        qs = qs.filter(Q(nome__icontains=query) | Q(cidade__icontains=query) | Q(estado__icontains=query))

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rebanho/propriedade_list.html', {
        'page_obj': page_obj,
        'search_query': query,
    })


@login_required
def propriedade_create(request):
    """Cadastro de nova propriedade rural."""
    if request.method == 'POST':
        form = PropriedadeForm(request.POST)
        if form.is_valid():
            propriedade = form.save(commit=False)
            propriedade.criador = request.user
            propriedade.save()
            messages.success(request, f'Propriedade "{propriedade.nome}" cadastrada com sucesso!')
            return redirect('propriedade_list')
        else:
            messages.error(request, 'Erro ao cadastrar propriedade. Verifique os dados informados.')
    else:
        form = PropriedadeForm()

    return render(request, 'rebanho/propriedade_form.html', {'form': form, 'acao': 'Cadastrar'})


@login_required
def propriedade_update(request, pk):
    """Edição de propriedade existente do usuário logado."""
    propriedade = get_object_or_404(Propriedade, pk=pk, criador=request.user)
    if request.method == 'POST':
        form = PropriedadeForm(request.POST, instance=propriedade)
        if form.is_valid():
            form.save()
            messages.success(request, f'Propriedade "{propriedade.nome}" atualizada com sucesso!')
            return redirect('propriedade_list')
        else:
            messages.error(request, 'Erro ao atualizar propriedade. Verifique os dados informados.')
    else:
        form = PropriedadeForm(instance=propriedade)

    return render(request, 'rebanho/propriedade_form.html', {
        'form': form,
        'propriedade': propriedade,
        'acao': 'Editar',
    })


@login_required
def propriedade_delete(request, pk):
    """Exclusão de propriedade do usuário logado."""
    propriedade = get_object_or_404(Propriedade, pk=pk, criador=request.user)
    total_animais = propriedade.animal_set.count()

    if request.method == 'POST':
        nome = propriedade.nome
        propriedade.delete()
        messages.success(request, f'Propriedade "{nome}" excluída com sucesso!')
        return redirect('propriedade_list')

    return render(request, 'rebanho/propriedade_confirm_delete.html', {
        'propriedade': propriedade,
        'total_animais': total_animais,
    })


# ==========================================
# ANIMAIS
# ==========================================

@login_required
def animal_list(request):
    """Lista todos os animais das propriedades do usuário logado com filtros e paginação."""
    query = request.GET.get('q', '').strip()
    propriedade_id = request.GET.get('propriedade', '')
    sexo = request.GET.get('sexo', '')

    qs = Animal.objects.filter(propriedade__criador=request.user).select_related('propriedade', 'pai', 'mae').order_by('brinco')

    if query:
        qs = qs.filter(Q(brinco__icontains=query) | Q(raca__icontains=query))
    if propriedade_id:
        qs = qs.filter(propriedade_id=propriedade_id)
    if sexo in ['M', 'F']:
        qs = qs.filter(sexo=sexo)

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    propriedades_usuario = Propriedade.objects.filter(criador=request.user)

    return render(request, 'rebanho/animal_list.html', {
        'page_obj': page_obj,
        'search_query': query,
        'propriedade_id': propriedade_id,
        'sexo_selecionado': sexo,
        'propriedades': propriedades_usuario,
    })


@login_required
def animal_detail(request, pk):
    """Ficha completa do animal com genealogia, pesagens, vacinações e reproduções."""
    animal = get_object_or_404(
        Animal.objects.select_related('propriedade', 'pai', 'mae'),
        pk=pk,
        propriedade__criador=request.user
    )

    pesagens = animal.pesagens.all().order_by('-data_pesagem')
    vacinas = animal.vacinas.all().order_by('-data_aplicacao')
    
    # Filhos
    filhos_como_pai = animal.filhos_pai.all()
    filhos_como_mae = animal.filhos_mae.all()
    filhos = (filhos_como_pai | filhos_como_mae).distinct()

    # Reproduções (caso seja fêmea)
    reproducoes = None
    if animal.sexo == 'F':
        reproducoes = animal.reproducao_set.all().order_by('-data_cobertura')

    # Movimentações do animal
    movimentacoes = animal.movimentacao_set.all().select_related('origem', 'destino').order_by('-data_movimentacao')

    # Última pesagem
    ultima_pesagem = pesagens.first()

    return render(request, 'rebanho/animal_detail.html', {
        'animal': animal,
        'pesagens': pesagens,
        'vacinas': vacinas,
        'filhos': filhos,
        'reproducoes': reproducoes,
        'movimentacoes': movimentacoes,
        'ultima_pesagem': ultima_pesagem,
    })


@login_required
def animal_cadastro(request):
    """Cadastro de novo animal."""
    # Verificar se o usuário possui ao menos uma propriedade cadastrada
    tem_propriedade = Propriedade.objects.filter(criador=request.user).exists()
    if not tem_propriedade:
        messages.warning(request, 'Você precisa cadastrar ao menos uma propriedade antes de cadastrar animais.')
        return redirect('propriedade_create')

    if request.method == 'POST':
        form = AnimalForm(request.POST, user=request.user)
        if form.is_valid():
            animal = form.save()
            messages.success(request, f'Animal brinco {animal.brinco} cadastrado com sucesso!')
            return redirect('animal_detail', pk=animal.pk)
        else:
            messages.error(request, 'Erro ao cadastrar o animal. Verifique os campos abaixo.')
    else:
        form = AnimalForm(user=request.user)

    return render(request, 'rebanho/animal_form.html', {'form': form, 'acao': 'Cadastrar'})


@login_required
def animal_update(request, pk):
    """Edição de dados de um animal existente."""
    animal = get_object_or_404(Animal, pk=pk, propriedade__criador=request.user)

    if request.method == 'POST':
        form = AnimalForm(request.POST, instance=animal, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Animal brinco {animal.brinco} atualizado com sucesso!')
            return redirect('animal_detail', pk=animal.pk)
        else:
            messages.error(request, 'Erro ao atualizar animal. Verifique os campos.')
    else:
        form = AnimalForm(instance=animal, user=request.user)

    return render(request, 'rebanho/animal_form.html', {
        'form': form,
        'animal': animal,
        'acao': 'Editar',
    })


@login_required
def animal_delete(request, pk):
    """Exclusão de animal do rebanho."""
    animal = get_object_or_404(Animal, pk=pk, propriedade__criador=request.user)

    if request.method == 'POST':
        brinco = animal.brinco
        animal.delete()
        messages.success(request, f'Animal brinco {brinco} excluído com sucesso!')
        return redirect('animal_list')

    return render(request, 'rebanho/animal_confirm_delete.html', {'animal': animal})


# ==========================================
# PESAGENS
# ==========================================

@login_required
def pesagem_list(request):
    """Lista as pesagens registradas para os animais do usuário."""
    query = request.GET.get('q', '').strip()
    qs = Pesagem.objects.filter(animal__propriedade__criador=request.user).select_related('animal', 'animal__propriedade').order_by('-data_pesagem')

    if query:
        qs = qs.filter(Q(animal__brinco__icontains=query) | Q(animal__raca__icontains=query))

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rebanho/pesagem_list.html', {
        'page_obj': page_obj,
        'search_query': query,
    })


@login_required
def pesagem_create(request):
    """Registro de nova pesagem."""
    animal_id = request.GET.get('animal_id')
    animal_obj = None
    if animal_id:
        animal_obj = get_object_or_404(Animal, pk=animal_id, propriedade__criador=request.user)

    if request.method == 'POST':
        form = PesagemForm(request.POST, user=request.user, animal=animal_obj)
        if form.is_valid():
            pesagem = form.save(commit=False)
            if animal_obj:
                pesagem.animal = animal_obj
            pesagem.save()
            messages.success(request, f'Pesagem de {pesagem.peso_kg} kg registrada para o animal {pesagem.animal.brinco}!')
            return redirect('animal_detail', pk=pesagem.animal.pk)
        else:
            messages.error(request, 'Erro ao registrar pesagem. Verifique os dados.')
    else:
        form = PesagemForm(user=request.user, animal=animal_obj)

    return render(request, 'rebanho/pesagem_form.html', {
        'form': form,
        'animal': animal_obj,
    })


@login_required
def pesagem_delete(request, pk):
    """Exclusão de pesagem."""
    pesagem = get_object_or_404(Pesagem, pk=pk, animal__propriedade__criador=request.user)
    animal_pk = pesagem.animal.pk

    if request.method == 'POST':
        pesagem.delete()
        messages.success(request, 'Registro de pesagem removido com sucesso!')
        return redirect('animal_detail', pk=animal_pk)

    return render(request, 'rebanho/confirm_delete.html', {
        'objeto': f'Pesagem de {pesagem.peso_kg} kg ({pesagem.animal.brinco})',
        'cancel_url': 'pesagem_list',
    })


# ==========================================
# VACINAÇÕES
# ==========================================

@login_required
def vacinacao_list(request):
    """Lista as vacinações dos animais do usuário."""
    query = request.GET.get('q', '').strip()
    qs = Vacinacao.objects.filter(animal__propriedade__criador=request.user).select_related('animal').order_by('-data_aplicacao')

    if query:
        qs = qs.filter(Q(animal__brinco__icontains=query) | Q(vacina__icontains=query))

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rebanho/vacinacao_list.html', {
        'page_obj': page_obj,
        'search_query': query,
    })


@login_required
def vacinacao_create(request):
    """Registro de nova vacinação."""
    animal_id = request.GET.get('animal_id')
    animal_obj = None
    if animal_id:
        animal_obj = get_object_or_404(Animal, pk=animal_id, propriedade__criador=request.user)

    if request.method == 'POST':
        form = VacinacaoForm(request.POST, user=request.user, animal=animal_obj)
        if form.is_valid():
            vacinacao = form.save(commit=False)
            if animal_obj:
                vacinacao.animal = animal_obj
            vacinacao.save()
            messages.success(request, f'Vacina "{vacinacao.vacina}" registrada com sucesso para {vacinacao.animal.brinco}!')
            return redirect('animal_detail', pk=vacinacao.animal.pk)
        else:
            messages.error(request, 'Erro ao registrar vacinação. Verifique os dados.')
    else:
        form = VacinacaoForm(user=request.user, animal=animal_obj)

    return render(request, 'rebanho/vacinacao_form.html', {
        'form': form,
        'animal': animal_obj,
    })


@login_required
def vacinacao_delete(request, pk):
    """Exclusão de vacinação."""
    vacinacao = get_object_or_404(Vacinacao, pk=pk, animal__propriedade__criador=request.user)
    animal_pk = vacinacao.animal.pk

    if request.method == 'POST':
        vacinacao.delete()
        messages.success(request, 'Registro de vacinação removido com sucesso!')
        return redirect('animal_detail', pk=animal_pk)

    return render(request, 'rebanho/confirm_delete.html', {
        'objeto': f'Vacinação de {vacinacao.vacina} ({vacinacao.animal.brinco})',
        'cancel_url': 'vacinacao_list',
    })


# ==========================================
# REPRODUÇÃO
# ==========================================

@login_required
def reproducao_list(request):
    """Lista os registros de reprodução do plantel do usuário."""
    query = request.GET.get('q', '').strip()
    qs = Reproducao.objects.filter(matriz__propriedade__criador=request.user).select_related('matriz').order_by('-data_cobertura')

    if query:
        qs = qs.filter(Q(matriz__brinco__icontains=query) | Q(observacao__icontains=query))

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rebanho/reproducao_list.html', {
        'page_obj': page_obj,
        'search_query': query,
    })


@login_required
def reproducao_create(request):
    """Registro de reprodução / cobertura / parto."""
    matriz_id = request.GET.get('matriz_id')
    matriz_obj = None
    if matriz_id:
        matriz_obj = get_object_or_404(Animal, pk=matriz_id, sexo='F', propriedade__criador=request.user)

    if request.method == 'POST':
        form = ReproducaoForm(request.POST, user=request.user, matriz=matriz_obj)
        if form.is_valid():
            rep = form.save(commit=False)
            if matriz_obj:
                rep.matriz = matriz_obj
            rep.save()
            messages.success(request, f'Registro reprodutivo da matriz {rep.matriz.brinco} salvo com sucesso!')
            return redirect('animal_detail', pk=rep.matriz.pk)
        else:
            messages.error(request, 'Erro ao salvar registro de reprodução. Verifique os dados.')
    else:
        form = ReproducaoForm(user=request.user, matriz=matriz_obj)

    return render(request, 'rebanho/reproducao_form.html', {
        'form': form,
        'matriz': matriz_obj,
    })


@login_required
def reproducao_delete(request, pk):
    """Exclusão de registro reprodutivo."""
    rep = get_object_or_404(Reproducao, pk=pk, matriz__propriedade__criador=request.user)
    matriz_pk = rep.matriz.pk

    if request.method == 'POST':
        rep.delete()
        messages.success(request, 'Registro reprodutivo removido com sucesso!')
        return redirect('animal_detail', pk=matriz_pk)

    return render(request, 'rebanho/confirm_delete.html', {
        'objeto': f'Registro reprodutivo da matriz {rep.matriz.brinco} em {rep.data_cobertura}',
        'cancel_url': 'reproducao_list',
    })
