from django.shortcuts import render

from ..models import User, Unit


def get_units(request):
    user = User.objects.get(id=1)
    units = Unit.objects.all()
    context = {'user': user,
               'units': units,
               'nav_active': 'guide',
               'title': 'Poradnik - Jednostki'}

    return render(request, 'helper/units.html', context)
