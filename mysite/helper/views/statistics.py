from datetime import datetime

from django.db import connection
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from ..models import User, UserStatisticsHistory


@login_required(login_url='helper:login')
def get_statistics(request, user_id):
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
               'title': 'Statystyki'}

    return render(request, 'helper/statistics.html', context)


def save_statistics(request):
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

    return redirect(reverse('helper:statistics', args=[user_id]))


def print_most_common_town_name():
    cursor = connection.cursor()
    cursor.execute(
        "SELECT town_name, COUNT(town_name) as val FROM helper_town GROUP BY town_name ORDER BY val ASC"
    )
    results = cursor.fetchall()
    for result in results:
        print(str(result[0]) + ' ' + str(result[1]))