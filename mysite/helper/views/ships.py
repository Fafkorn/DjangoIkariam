from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import User, Ship, DefaultUsersConnection


@login_required(login_url='helper:login')
def get_ships(request):
    connected_user = DefaultUsersConnection.objects.filter(auth_user=request.user.id)
    user = connected_user[0] if connected_user else User.objects.get(pk=1)
    ships = Ship.objects.all()
    context = {'user': user,
               'ships': ships,
               'nav_active': 'guide',
               'title': 'Poradnik - Statki'}

    return render(request, 'helper/ships.html', context)
