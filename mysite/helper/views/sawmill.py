from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from mysite.helper.models import DefaultUsersConnection, User, SawMillWorkers, MineWorkers


@login_required(login_url='helper:login')
def get_sawmill(request):
    connected_user = DefaultUsersConnection.objects.filter(auth_user=request.user.id)
    user = connected_user[0] if connected_user else User.objects.get(pk=1)
    sawmills = SawMillWorkers.objects.filter(level__gt=0)
    mines = MineWorkers.objects.filter(level__gt=0)
    context = {'user': user,
               'nav_active': 'guide',
               'sawmills': sawmills,
               'mines': mines,
               'title': 'Poradnik - Tartak/Kopalnia'}
    return render(request, 'helper/sawmill.html', context)
