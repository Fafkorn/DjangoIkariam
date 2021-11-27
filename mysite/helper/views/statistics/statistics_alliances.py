from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from mysite import settings
from mysite.helper.models import User, AllianceHistory, Alliance


server = settings.ACTIVE_SERVER


@login_required(login_url='helper:login')
def get_statistics_alliances(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    top_alliance_histories = get_alliance_histories()

    context = {'user': user,
               'nav_active': 'statistics',
               'alliance_histories': top_alliance_histories,
               'title': 'Statystyki - Sojusze'}

    return render(request, 'helper/statistics/statistics_alliances.html', context)


def get_alliance_histories():
    records = AllianceHistory.objects.all().order_by('-time')
    if records:
        last_update_date = records[0].time
        top_alliances = AllianceHistory.objects.filter(time__year=last_update_date.year,
                                                       time__month=last_update_date.month,
                                                       time__day=last_update_date.day,
                                                       alliance__server=server).order_by('-points')[:10]
        top_alliance_histories = []
        for alliance in top_alliances:
            alliance_data = AllianceHistory.objects.filter(alliance__id=alliance.alliance.id)
            if alliance_data:
                top_alliance_histories.append(alliance_data)
        return top_alliance_histories
    else:
        return []


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
    return redirect(reverse('helper:statistics_alliances', args=[user_id]))
