from django.shortcuts import render

from ...models import User, Ship


def get_ships(request):
    user = User.objects.get(id=1)
    ships = Ship.objects.all()
    context = {'user': user,
               'ships': ships,
               'nav_active': 'guide',
               'title': 'Poradnik - Statki'}

    return render(request, 'helper/guide/ships.html', context)
