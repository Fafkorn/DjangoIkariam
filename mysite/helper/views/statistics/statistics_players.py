from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from mysite.helper.models import User, UserStatisticsHistory


@login_required(login_url='helper:login')
def get_statistics_players(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    all_users = User.objects.all().count()
    active_users = User.objects.filter(user_status__id=1).count()
    inactive_users = User.objects.filter(user_status__id=2).count()
    on_vacation_users = User.objects.filter(user_status__id=4).count()
    deleted_users = User.objects.filter(user_status__id=3).count()

    user_statistics_histories = UserStatisticsHistory.objects.all()

    context = {'user': user,
               'nav_active': 'statistics',
               'all_users': all_users,
               'active_users': active_users,
               'inactive_users': inactive_users,
               'on_vacation_users': on_vacation_users,
               'deleted_users': deleted_users,
               'user_statistics_histories': user_statistics_histories,
               'title': 'Statystyki - Gracze'}

    return render(request, 'helper/statistics/statistics_players.html', context)


def save_users_statistics(request):
    user_id = request.POST['user_id']

    active_users = User.objects.filter(user_status__id=1).count()
    inactive_users = User.objects.filter(user_status__id=2).count()
    on_vacation_users = User.objects.filter(user_status__id=4).count()
    deleted_users = User.objects.filter(user_status__id=3).count()

    today = datetime.now()
    user_statistics_history = UserStatisticsHistory.objects.filter(time__year=today.year, time__month=today.month,
                                                                   time__day=today.day)

    if user_statistics_history:
        user_statistics_history = user_statistics_history[0]
    else:
        user_statistics_history = UserStatisticsHistory()
        user_statistics_history.time = today

    user_statistics_history.active_users = active_users
    user_statistics_history.inactive_users = inactive_users
    user_statistics_history.on_vacation_users = on_vacation_users
    user_statistics_history.deleted_users = deleted_users
    user_statistics_history.save()

    return redirect(reverse('helper:statistics_players', args=[user_id]))
