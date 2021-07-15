from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import User, Unit


@login_required(login_url='helper:login')
def get_units(request):
    user = User.objects.get(id=1)
    units = Unit.objects.all()
    context = {'user': user,
               'units': units,
               'nav_active': 'guide',
               'title': 'Poradnik - Jednostki'}

    return render(request, 'helper/units.html', context)
