from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import User, Ship


@login_required(login_url='helper:login')
def get_ships(request):
    user = User.objects.get(id=1)
    ships = Ship.objects.all()
    context = {'user': user,
               'ships': ships,
               'nav_active': 'guide',
               'title': 'Poradnik - Statki'}

    return render(request, 'helper/ships.html', context)
