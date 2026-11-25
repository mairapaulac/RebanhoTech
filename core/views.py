import json
import urllib.request
from datetime import date
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnuncioForm, MovimentacaoForm, NegociacaoForm, UserRegisterForm
from .models import Anuncio, Movimentacao, Negociacao, Notificacao
from rebanho.models import Animal, Propriedade


# ==========================================
# AUTENTICAÇÃO E REGISTRO
# ==========================================

def register(request):
    """Cadastro de novo usuário / criador no sistema."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
            )
            # Notificação de boas-vindas
            Notificacao.objects.create(
                usuario=user,
                titulo="Bem-vindo ao RebanhoTech!",
                mensagem=f"Olá, {user.first_name or user.username}! Sua conta foi criada com sucesso. Comece cadastrando sua primeira propriedade rural no menu Propriedades."
            )
            messages.success(request, f'Conta criada com sucesso! Bem-vindo(a), {user.username}.')
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Não foi possível concluir o cadastro. Verifique os erros no formulário.')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================

@login_required
def dashboard(request):
    """
    Painel de controle com visão geral do rebanho, indicadores,
    movimentações recentes, notificações e cotação do mercado financeiro (API Externa).
    """
    user = request.user
    
    # Indicadores principais
    total_propriedades = Propriedade.objects.filter(criador=user).count()
    animais_qs = Animal.objects.filter(propriedade__criador=user)
    total_animais = animais_qs.count()
    machos_count = animais_qs.filter(sexo='M').count()
    femeas_count = animais_qs.filter(sexo='F').count()

    anuncios_ativos_count = Anuncio.objects.filter(vendedor=user, ativo=True).count()
    propostas_recebidas_count = Negociacao.objects.filter(anuncio__vendedor=user, status='EM_ANDAMENTO').count()
    notificacoes_nao_lidas = Notificacao.objects.filter(usuario=user, lida=False).count()

    # Distribuição por raça (top 5)
    racas_dist = (
        animais_qs.values('raca')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    # Últimas movimentações
    ultimas_movimentacoes = (
        Movimentacao.objects.filter(Q(origem__criador=user) | Q(destino__criador=user))
        .select_related('animal', 'origem', 'destino')
        .order_by('-data_movimentacao')[:5]
    )

    # Últimas notificações
    ultimas_notificacoes = (
        Notificacao.objects.filter(usuario=user)
        .order_by('-data_criacao')[:5]
    )

    # Requisito Desejável: Consumo de API REST Externa (Cotações Econômicas / Financeiras)
    cotacoes = None
    try:
        url = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL"
        req = urllib.request.Request(url, headers={'User-Agent': 'RebanhoTech/1.0'})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            cotacoes = {
                'dolar': data.get('USDBRL', {}),
                'euro': data.get('EURBRL', {}),
            }
    except Exception:
        cotacoes = None

    return render(request, 'core/dashboard.html', {
        'total_propriedades': total_propriedades,
        'total_animais': total_animais,
        'machos_count': machos_count,
        'femeas_count': femeas_count,
        'anuncios_ativos_count': anuncios_ativos_count,
        'propostas_recebidas_count': propostas_recebidas_count,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'racas_dist': racas_dist,
        'ultimas_movimentacoes': ultimas_movimentacoes,
        'ultimas_notificacoes': ultimas_notificacoes,
        'cotacoes': cotacoes,
    })


# ==========================================
# MOVIMENTAÇÕES
# ==========================================

@login_required
def movimentacao_list(request):
    """Lista as transferências de animais entre propriedades do usuário."""
    query = request.GET.get('q', '').strip()
    qs = Movimentacao.objects.filter(
        Q(origem__criador=request.user) | Q(destino__criador=request.user)
    ).select_related('animal', 'origem', 'destino').order_by('-data_movimentacao')

    if query:
        qs = qs.filter(
            Q(animal__brinco__icontains=query) |
            Q(motivo__icontains=query) |
            Q(origem__nome__icontains=query) |
            Q(destino__nome__icontains=query)
        )

    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/movimentacao_list.html', {
        'page_obj': page_obj,
        'search_query': query,
    })


@login_required
def movimentacao_create(request):
    """
    Formulário para transferir animal entre propriedades.
    Ao salvar a movimentação, a propriedade atual do animal é atualizada.
    """
    animal_id = request.GET.get('animal_id')
    animal_obj = None
    if animal_id:
        animal_obj = get_object_or_404(Animal, pk=animal_id, propriedade__criador=request.user)

    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, user=request.user, animal=animal_obj)
        if form.is_valid():
            with transaction.atomic():
                movimentacao = form.save()
                # Atualizar a propriedade atual do animal para a propriedade de destino
                animal = movimentacao.animal
                animal.propriedade = movimentacao.destino
                animal.save(update_fields=['propriedade'])

            messages.success(
                request,
                f'Movimentação realizada com sucesso! O animal {animal.brinco} foi transferido para a propriedade "{movimentacao.destino.nome}".'
            )
            return redirect('movimentacao_list')
        else:
            messages.error(request, 'Erro ao registrar movimentação. Verifique os campos informados.')
    else:
        form = MovimentacaoForm(user=request.user, animal=animal_obj)

    return render(request, 'core/movimentacao_form.html', {
        'form': form,
        'animal': animal_obj,
    })


# ==========================================
# MARKETPLACE (ANÚNCIOS E NEGOCIAÇÕES)
# ==========================================

def anuncio_list(request):
    """Vitrine pública de anúncios com busca por texto, raça e faixa de preço."""
    query = request.GET.get('q', '').strip()
    raca = request.GET.get('raca', '').strip()
    preco_max = request.GET.get('preco_max', '').strip()

    qs = Anuncio.objects.filter(ativo=True).select_related('vendedor', 'animal', 'animal__propriedade').order_by('-data_publicacao')

    if query:
        qs = qs.filter(Q(titulo__icontains=query) | Q(descricao__icontains=query) | Q(animal__raca__icontains=query))
    if raca:
        qs = qs.filter(animal__raca__icontains=raca)
    if preco_max:
        try:
            qs = qs.filter(preco__lte=float(preco_max))
        except ValueError:
            pass

    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/anuncio_list.html', {
        'page_obj': page_obj,
        'search_query': query,
        'raca_selecionada': raca,
        'preco_max': preco_max,
    })


def anuncio_detail(request, pk):
    """
    Detalhes do anúncio, animal ofertado, vendedor e envio/gestão de propostas.
    """
    anuncio = get_object_or_404(
        Anuncio.objects.select_related('vendedor', 'animal', 'animal__propriedade'),
        pk=pk
    )

    # Se o usuário logado for o vendedor, ele vê todas as propostas recebidas
    propostas_recebidas = None
    if request.user.is_authenticated and request.user == anuncio.vendedor:
        propostas_recebidas = anuncio.negociacao_set.select_related('comprador').order_by('-data_proposta')

    # Se o usuário for um comprador autenticado e diferente do vendedor
    proposta_form = None
    proposta_usuario = None
    if request.user.is_authenticated and request.user != anuncio.vendedor:
        proposta_usuario = anuncio.negociacao_set.filter(comprador=request.user).order_by('-data_proposta').first()
        if request.method == 'POST' and anuncio.ativo:
            proposta_form = NegociacaoForm(request.POST)
            if proposta_form.is_valid():
                negociacao = proposta_form.save(commit=False)
                negociacao.anuncio = anuncio
                negociacao.comprador = request.user
                negociacao.status = 'EM_ANDAMENTO'
                negociacao.save()

                # Notificar o vendedor da proposta recebida
                Notificacao.objects.create(
                    usuario=anuncio.vendedor,
                    titulo="Nova Proposta de Compra Recebida!",
                    mensagem=(
                        f"O criador {request.user.first_name or request.user.username} enviou uma proposta de "
                        f"R$ {negociacao.valor_proposto:.2f} para o seu anúncio '{anuncio.titulo}'."
                    )
                )

                messages.success(request, f'Sua proposta de R$ {negociacao.valor_proposto:.2f} foi enviada com sucesso ao vendedor!')
                return redirect('anuncio_detail', pk=anuncio.pk)
            else:
                messages.error(request, 'Erro ao enviar proposta. Verifique o valor informado.')
        else:
            proposta_form = NegociacaoForm(initial={'valor_proposto': anuncio.preco})

    # Histórico de pesagens e vacinas recentes do animal
    pesagens = anuncio.animal.pesagens.order_by('-data_pesagem')[:3]
    vacinas = anuncio.animal.vacinas.order_by('-data_aplicacao')[:3]

    return render(request, 'core/anuncio_detail.html', {
        'anuncio': anuncio,
        'propostas_recebidas': propostas_recebidas,
        'proposta_form': proposta_form,
        'proposta_usuario': proposta_usuario,
        'pesagens': pesagens,
        'vacinas': vacinas,
    })


@login_required
def anuncio_create(request):
    """Cadastro de novo anúncio pelo vendedor para seus animais."""
    animal_id = request.GET.get('animal_id')
    animal_obj = None
    if animal_id:
        animal_obj = get_object_or_404(Animal, pk=animal_id, propriedade__criador=request.user)

    if request.method == 'POST':
        form = AnuncioForm(request.POST, user=request.user, animal=animal_obj)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.vendedor = request.user
            if animal_obj:
                anuncio.animal = animal_obj
            anuncio.save()
            messages.success(request, f'Anúncio "{anuncio.titulo}" publicado com sucesso no Marketplace!')
            return redirect('anuncio_detail', pk=anuncio.pk)
        else:
            messages.error(request, 'Erro ao publicar anúncio. Verifique os dados preenchidos.')
    else:
        form = AnuncioForm(user=request.user, animal=animal_obj)

    return render(request, 'core/anuncio_form.html', {
        'form': form,
        'animal': animal_obj,
        'acao': 'Publicar',
    })


@login_required
def anuncio_update(request, pk):
    """Edição de anúncio existente pertencente ao vendedor."""
    anuncio = get_object_or_404(Anuncio, pk=pk, vendedor=request.user)

    if request.method == 'POST':
        form = AnuncioForm(request.POST, instance=anuncio, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Anúncio "{anuncio.titulo}" atualizado com sucesso!')
            return redirect('anuncio_detail', pk=anuncio.pk)
        else:
            messages.error(request, 'Erro ao atualizar anúncio. Verifique os dados preenchidos.')
    else:
        form = AnuncioForm(instance=anuncio, user=request.user)

    return render(request, 'core/anuncio_form.html', {
        'form': form,
        'anuncio': anuncio,
        'acao': 'Editar',
    })


@login_required
def anuncio_delete(request, pk):
    """Exclusão de anúncio pelo vendedor."""
    anuncio = get_object_or_404(Anuncio, pk=pk, vendedor=request.user)

    if request.method == 'POST':
        titulo = anuncio.titulo
        anuncio.delete()
        messages.success(request, f'Anúncio "{titulo}" excluído com sucesso!')
        return redirect('meus_anuncios')

    return render(request, 'core/anuncio_confirm_delete.html', {'anuncio': anuncio})


@login_required
def meus_anuncios(request):
    """Lista todos os anúncios criados pelo usuário logado com contador de propostas."""
    qs = Anuncio.objects.filter(vendedor=request.user).annotate(
        total_propostas=Count('negociacao')
    ).order_by('-data_publicacao')

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/meus_anuncios.html', {'page_obj': page_obj})


@login_required
def minhas_propostas(request):
    """Lista as propostas enviadas pelo usuário em anúncios de terceiros."""
    qs = Negociacao.objects.filter(comprador=request.user).select_related('anuncio', 'anuncio__vendedor').order_by('-data_proposta')

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/minhas_propostas.html', {'page_obj': page_obj})


@login_required
def aceitar_proposta(request, pk):
    """Vendedor aceita uma proposta de compra no anúncio."""
    proposta = get_object_or_404(Negociacao, pk=pk, anuncio__vendedor=request.user)

    if request.method == 'POST':
        with transaction.atomic():
            proposta.status = 'CONCLUIDA'
            proposta.save(update_fields=['status'])

            anuncio = proposta.anuncio
            anuncio.ativo = False
            anuncio.save(update_fields=['ativo'])

            # Notificar o comprador que a proposta foi aceita
            Notificacao.objects.create(
                usuario=proposta.comprador,
                titulo="Proposta Aceita!",
                mensagem=(
                    f"Parabéns! Sua proposta de R$ {proposta.valor_proposto:.2f} no anúncio '{anuncio.titulo}' "
                    f"foi ACEITA pelo vendedor {request.user.first_name or request.user.username}. Entre em contato para finalizar a entrega."
                )
            )

        messages.success(request, f'Proposta de R$ {proposta.valor_proposto:.2f} aceita! O anúncio foi marcado como finalizado.')
        return redirect('anuncio_detail', pk=proposta.anuncio.pk)

    return redirect('anuncio_detail', pk=proposta.anuncio.pk)


@login_required
def recusar_proposta(request, pk):
    """Vendedor recusa ou cancela uma proposta de compra."""
    proposta = get_object_or_404(Negociacao, pk=pk, anuncio__vendedor=request.user)

    if request.method == 'POST':
        proposta.status = 'CANCELADA'
        proposta.save(update_fields=['status'])

        # Notificar o comprador
        Notificacao.objects.create(
            usuario=proposta.comprador,
            titulo="Proposta Recusada",
            mensagem=(
                f"Sua proposta de R$ {proposta.valor_proposto:.2f} no anúncio '{proposta.anuncio.titulo}' "
                f"foi recusada pelo vendedor."
            )
        )

        messages.info(request, f'Proposta de {proposta.comprador.username} recusada.')
        return redirect('anuncio_detail', pk=proposta.anuncio.pk)

    return redirect('anuncio_detail', pk=proposta.anuncio.pk)


# ==========================================
# NOTIFICAÇÕES
# ==========================================

@login_required
def notificacao_list(request):
    """Tela com histórico de notificações do usuário."""
    qs = Notificacao.objects.filter(usuario=request.user).order_by('-data_criacao')

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/notificacao_list.html', {'page_obj': page_obj})


@login_required
def notificacao_marcar_lida(request, pk):
    """Marca uma notificação individual como lida."""
    notificacao = get_object_or_404(Notificacao, pk=pk, usuario=request.user)
    notificacao.lida = True
    notificacao.save(update_fields=['lida'])
    return redirect('notificacao_list')


@login_required
def notificacoes_marcar_todas_lidas(request):
    """Marca todas as notificações pendentes do usuário como lidas."""
    Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
    messages.success(request, 'Todas as notificações foram marcadas como lidas.')
    return redirect('notificacao_list')


# ==========================================
# REQUISITO DESEJÁVEL: FORNECER API REST
# ==========================================

def api_anuncios(request):
    """
    Endpoint REST que expõe os anúncios ativos para integração com outros sistemas ou colegas da disciplina.
    """
    anuncios = Anuncio.objects.filter(ativo=True).select_related('vendedor', 'animal')
    data = []
    for a in anuncios:
        data.append({
            'id': a.id,
            'titulo': a.titulo,
            'preco': float(a.preco),
            'vendedor': a.vendedor.username,
            'animal_brinco': a.animal.brinco,
            'animal_raca': a.animal.raca,
            'animal_sexo': a.animal.get_sexo_display(),
            'data_publicacao': a.data_publicacao.isoformat(),
        })
    return JsonResponse({'total': len(data), 'anuncios': data})


def api_animais(request):
    """
    Endpoint REST que expõe a lista de animais para consumo externo.
    """
    animais = Animal.objects.select_related('propriedade')[:100]
    data = []
    for an in animais:
        data.append({
            'id': an.id,
            'brinco': an.brinco,
            'raca': an.raca,
            'sexo': an.sexo,
            'data_nascimento': an.data_nascimento.isoformat() if an.data_nascimento else None,
            'propriedade': an.propriedade.nome,
            'cidade': an.propriedade.cidade,
            'uf': an.propriedade.estado,
        })
    return JsonResponse({'total': len(data), 'animais': data})


def api_estatisticas(request):
    """
    Endpoint REST que expõe estatísticas agregadas do sistema.
    """
    total_animais = Animal.objects.count()
    total_propriedades = Propriedade.objects.count()
    total_anuncios_ativos = Anuncio.objects.filter(ativo=True).count()
    dist_raca = list(Animal.objects.values('raca').annotate(quantidade=Count('id')).order_by('-quantidade'))

    return JsonResponse({
        'total_animais': total_animais,
        'total_propriedades': total_propriedades,
        'total_anuncios_ativos': total_anuncios_ativos,
        'distribuicao_racas': dist_raca,
    })
