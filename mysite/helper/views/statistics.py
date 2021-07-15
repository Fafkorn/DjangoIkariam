from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import User


@login_required(login_url='helper:login')
def get_statistics(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    all_users = User.objects.all().count()
    active_users = User.objects.filter(user_status__id=1).count()
    inactive_users = User.objects.filter(user_status__id=2).count()
    on_vacation__users = User.objects.filter(user_status__id=4).count()
    deleted_users = User.objects.filter(user_status__id=3).count()

    context = {'user': user,
               'nav_active': 'statistics',
               'all_users': all_users,
               'active_users': active_users,
               'inactive_users': inactive_users,
               'on_vacation__users': on_vacation__users,
               'deleted_users': deleted_users,
               'title': 'Statystyki'}

    return render(request, 'helper/statistics.html', context)
