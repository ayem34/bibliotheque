from .models import Notification

def notifications_context(request):
    """Ajoute les notifications non lues de l'utilisateur connecté au contexte global."""
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(utilisateur=request.user, est_lu=False).order_by('-date_envoi')
        non_lues_count = notifications.count()
        return {
            'notifications': notifications,
            'non_lues_count': non_lues_count
        }
    return {'notifications': [], 'non_lues_count': 0}