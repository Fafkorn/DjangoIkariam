from datetime import datetime

from django.db import connection
from django.db.models import Count, Q, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from ..models import User, UserStatisticsHistory, Alliance, AllianceHistory


@login_required(login_url='helper:login')
def get_statistics(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    all_users = User.objects.all().count()
    active_users = User.objects.filter(user_status__id=1).count()
    inactive_users = User.objects.filter(user_status__id=2).count()
    on_vacation_users = User.objects.filter(user_status__id=4).count()
    deleted_users = User.objects.filter(user_status__id=3).count()

    user_statistics_histories = UserStatisticsHistory.objects.all()
    top_alliance_histories = get_alliance_histories()

    context = {'user': user,
               'nav_active': 'statistics',
               'all_users': all_users,
               'active_users': active_users,
               'inactive_users': inactive_users,
               'on_vacation_users': on_vacation_users,
               'deleted_users': deleted_users,
               'user_statistics_histories': user_statistics_histories,
               'alliance_histories': top_alliance_histories,
               'title': 'Statystyki'}

    return render(request, 'helper/statistics.html', context)


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

    return redirect(reverse('helper:statistics', args=[user_id]))


def save_alliances_statistics(request):
    user_id = request.POST['user_id']

    today = datetime.now()
    AllianceHistory.objects.filter(time__year=today.year, time__month=today.month, time__day=today.day).delete()

    alliance_histories_to_save = []
    alliances_data = Alliance.objects.annotate(members=Count('user', filter=~Q(user__user_status__id=3))).annotate(score=Sum('user__score', filter=~Q(user__user_status__id=3))).order_by('members')

    for data in alliances_data:
        alliance_history = AllianceHistory()
        alliance_history.alliance = Alliance.objects.get(pk=data.id)
        alliance_history.time = today
        alliance_history.members = data.members
        if data.score:
            alliance_history.points = data.score
        else:
            alliance_history.points = 0
        alliance_histories_to_save.append(alliance_history)
    AllianceHistory.objects.bulk_create(alliance_histories_to_save)
    return redirect(reverse('helper:statistics', args=[user_id]))

def get_alliance_histories():
    records = AllianceHistory.objects.all().order_by('-time')
    if records:
        last_update_date = records[0].time
        top_alliances = AllianceHistory.objects.filter(time__year=last_update_date.year,
                                                       time__month=last_update_date.month,
                                                       time__day=last_update_date.day).order_by('-points')[:10]
        top_alliance_histories = []
        for alliance in top_alliances:
            alliance_data = AllianceHistory.objects.filter(alliance__id=alliance.alliance.id)
            if alliance_data:
                top_alliance_histories.append(alliance_data)
        return top_alliance_histories
    else:
        return []


def print_most_common_town_name():
    cursor = connection.cursor()
    cursor.execute(
        "SELECT town_name, COUNT(town_name) as val FROM helper_town GROUP BY town_name ORDER BY val ASC"
    )
    results = cursor.fetchall()
    for result in results:
        print(str(result[0]) + ' ' + str(result[1]))