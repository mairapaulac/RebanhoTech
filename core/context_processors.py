from .models import Notificacao

def notifications_context(request):
    """
    Context processor para disponibilizar a contagem de notificações não lidas
    globalmente para os templates (especialmente para a navbar).
    """
    if request.user.is_authenticated:
        count = Notificacao.objects.filter(usuario=request.user, lida=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
