from django.contrib.auth.decorators import login_required
from django.db.models import Subquery, OuterRef
from django.shortcuts import get_object_or_404, render
from django.utils.dateformat import DateFormat

from mysite.helper.models import User, UserHistory
from datetime import datetime, timedelta


@login_required(login_url='helper:login')
def get_statistics_scores(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    selected_rank_type = request.GET.get('rank_type', 'score')
    selected_date = request.GET.get('selected_date', '')
    if not selected_date:
        selected_date = datetime.today() - timedelta(days=60)
        df = DateFormat(selected_date)
        selected_date = df.format('Y-m-d')

    best_players = get_best_players(selected_rank_type, selected_date)

    context = {'user': user,
               'nav_active': 'statistics',
               'selected_rank_type': selected_rank_type,
               'selected_date': selected_date,
               'rank_types': get_displayable_rank_type_names(),
               'best_players': best_players,
               'title': 'Statystyki - Punkty'}

    return render(request, 'helper/statistics/statistics_scores.html', context)


def get_best_players(ranking_type: str, selected_date: datetime):
    rows = User.objects.all().annotate(
        inc=Subquery(UserHistory.objects.filter(user__id=OuterRef('id')).order_by('-time').values(ranking_type)[:1]) -
        Subquery(UserHistory.objects.filter(user__id=OuterRef('id'), time__gte=selected_date).order_by('time').values(ranking_type)[:1])
    ).annotate(
        ranking_score=Subquery(UserHistory.objects.filter(user__id=OuterRef('id')).order_by('-time').values(ranking_type)[:1])
    ).order_by('-inc')[:50]
    return rows


def get_displayable_rank_type_names():
    return [["score", "Całkowity wynik"],
        ["master_builders", "Mistrzowie budowy"],
        ["building_levels", "Poziomy budynków"],
        ["scientists", "Naukowcy"],
        ["research_level", "Poziomy badań"],
        ["generals", "Generałowie"],
        ["gold", "Złoto"],
        ["offensive", "Punkty ofensywy"],
        ["defensive", "Punkty obrony"],
        ["trading", "Handlarz"],
        ["resources", "Surowce"],
        ["donations", "Datki"],
        ["piracy", "Punkty abordażu"]]
