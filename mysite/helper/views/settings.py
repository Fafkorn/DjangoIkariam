from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from ..models import User, DefaultUsersConnection


@login_required(login_url='helper:login')
def get_settings(request):
    connected_user = DefaultUsersConnection.objects.filter(auth_user=request.user.id)
    user = connected_user[0] if connected_user else User.objects.get(pk=1)
    context = {
        'user': user,
        'title': 'Ustawienia'
    }

    if request.method == 'POST':
        set_connection(request)
    return render(request, 'helper/settings.html', context)


def set_connection(request):
    users = User.objects.filter(user_name=request.POST.get('username'))
    if not users:
        messages.error(request, 'Podany użytkownik nie istnieje')
    else:
        user = users[0]
        auth_user = request.user.id
        DefaultUsersConnection.objects.filter(auth_user=auth_user).delete()
        default_users_connection = DefaultUsersConnection(auth_user=auth_user, game_user=user)
        default_users_connection.save()
        messages.success(request, 'Konta zostały połączone')
