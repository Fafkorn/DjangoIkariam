from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import User, Unit, DefaultUsersConnection


@login_required(login_url='helper:login')
def get_units(request):
    connected_user = DefaultUsersConnection.objects.filter(auth_user=request.user.id)
    user = connected_user[0] if connected_user else User.objects.get(pk=1)
    units = Unit.objects.all()
    context = {'user': user,
               'units': units,
               'nav_active': 'guide',
               'title': 'Poradnik - Jednostki'}

    return render(request, 'helper/units.html', context)
