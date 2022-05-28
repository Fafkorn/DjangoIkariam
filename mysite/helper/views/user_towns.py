from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q, Sum
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils.dateformat import DateFormat

from ..models import User, Town, Island, Resource, UserHistory

from mysite import settings
from django.contrib.auth.decorators import login_required

server = settings.ACTIVE_SERVER


@login_required(login_url='helper:login')
def get_user_towns(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.last_visit = datetime.now()
    user.save()

    towns = Town.objects.filter(user__id=user_id, island__server=server, is_deleted=False).order_by('island')

    wood_workers = get_workers(user_id)
    wine_workers = get_mine_workers(user_id, 2)
    marble_workers = get_mine_workers(user_id, 3)
    crystal_workers = get_mine_workers(user_id, 4)
    sulfur_workers = get_mine_workers(user_id, 5)

    username = request.GET.get('username', '')
    alliance_tag = request.GET.get('alliance_tag', '')
    search_type = request.GET.get('search_type', '')
    search_value = request.GET.get('search_value', 0)

    rank_type = request.GET.get('rank_type', 'score')
    compare_user_names = request.GET.getlist('compare_user', '')
    selected_names = []
    selected_date = request.GET.get('selected_date', '')
    if not selected_date:
        selected_date = datetime.today() - timedelta(days=365)
        df = DateFormat(selected_date)
        selected_date = df.format('Y-m-d')
    chart_data = get_chart_data(user.id, rank_type, selected_date)

    compare_users = []
    for compare_user_name in compare_user_names:
        user_to_compare = User.objects.filter(user_name=compare_user_name)
        if user_to_compare and len(compare_user_name) > 0:
            selected_names.append(user_to_compare[0].user_name)
            compare_users.append(user_to_compare[0])
    compare_data = []
    for compare_user in compare_users:
        data = get_chart_data(compare_user.id, rank_type, selected_date)
        structure = {'data': data,
                     'username': compare_user.user_name,
                     'difference': get_points_difference(data)}
        compare_data.append(structure)

    context = {
        'user': user,
        'user_id': user_id,
        'username': username,
        'alliance_tag': alliance_tag,
        'search_type': search_type,
        'search_type_display': get_displayable_search_name(search_type),
        'selected_rank_type': rank_type,
        'rank_types': get_displayable_rank_type_names(),
        'search_value': search_value,
        'towns': towns,
        'wood_workers': wood_workers,
        'wine_workers': wine_workers,
        'marble_workers': marble_workers,
        'crystal_workers': crystal_workers,
        'sulfur_workers': sulfur_workers,
        'all_workers': wood_workers + wine_workers + marble_workers + crystal_workers + sulfur_workers,
        'all_islands': get_coordinates(Island.objects.filter(server=server)),
        'occupied_islands': get_occupied_islands(),
        'own_islands': get_coordinates_for_towns(towns),
        'searched_islands': get_searched_coordinates(username, alliance_tag, search_type, search_value),
        'nav_active': 'user_towns',
        'title': 'Miasta - ' + user.user_name,
        'chart_data': chart_data,
        'selected_date': selected_date,
        'user_points_income': get_points_difference(chart_data),
        'compare_datas': compare_data,
        'compare_user_names': selected_names,
        'clipboard': get_towns_as_text(towns)
    }
    return render(request, 'helper/user_towns.html', context)


def get_points_difference(data) -> int:
    if data:
        return data[len(data) - 1][1] - data[0][1]
    return 0


def add_town(request, user_id):
    island = get_island(request.POST['x'], request.POST['y'])
    new_town = Town(user_id=user_id,
                    town_name=request.POST['town_name'],
                    island=island)
    new_town.save()
    return HttpResponseRedirect(reverse('helper:user_towns', args=(user_id,)))


def update_town(request, user_id):
    town = Town.objects.get(pk=request.POST['town_id'])
    island = get_island(request.POST['town_x'], request.POST['town_y'])
    town.town_name = request.POST['town_name']
    town.island = island
    town.save()
    return HttpResponseRedirect(reverse('helper:user_towns', args=(user_id,)))


def get_island(x, y):
    island = Island.objects.filter(x=x, y=y)
    resource = Resource.objects.get(pk=1)
    if island.count() == 1:
        return island[0]
    else:
        island = Island(x=x, y=y,
                        wood_level=1, wood_resource=resource,
                        luxury_level=1, luxury_resource=resource, server=server)
        island.save()
        return island


def delete_town(request, user_id):
    Town.objects.filter(pk=request.POST['town_id']).delete()
    return HttpResponseRedirect(reverse('helper:user_towns', args=(user_id,)))


def get_workers(user_id):
    workers = Town.objects.filter(user__id=user_id, island__server=server).annotate(workers=Sum('island__wood_level__workers')).aggregate(sum=Sum('workers'))['sum']
    if not workers:
        return 0
    return workers


def get_mine_workers(user_id, mine_type):
    workers = Town.objects.filter(user__id=user_id, island__luxury_resource_id=mine_type, island__server=server).annotate(workers=Sum('island__luxury_level__workers')).aggregate(sum=Sum('workers'))['sum']
    if not workers:
        return 0
    return workers


def get_coordinates(islands):
    coords = []
    for island in islands:
        coords.append([island.x, island.y])
    return coords


def get_coordinates_for_towns(towns):
    coords = []
    for town in towns:
        coords.append([town.island.x, town.island.y])
    return coords


def get_searched_coordinates(username, alliance_tag, search_type, search_value):
    if username != '':
        return get_player_coords(username)
    if alliance_tag != '':
        return get_alliance_coords(alliance_tag)
    if search_type != '':
        return get_selected_islands(search_type, search_value)
    return []


def get_player_coords(username):
    towns = Town.objects.filter(Q(user__user_name=username, user__server=server))
    return get_coordinates_for_towns(towns)


def get_alliance_coords(alliance_tag):
    towns = Town.objects.filter(Q(user__alliance__tag=alliance_tag, user__server=server, island__server=server))
    return get_coordinates_for_towns(towns)


def get_occupied_islands():
    occupied_islands = Island.objects.all().annotate(towns=Count('town', filter=~Q(town__user__user_status__id=3, town__is_deleted=False))).filter(towns__gt=0, server=server)
    coords = []

    for island in occupied_islands:
        coords.append([island.x, island.y])
    return coords


def get_selected_islands(search_type, search_value):
    islands = []
    coords = []
    if search_type == 'sawmill_above':
        islands = Island.objects.all().filter(wood_level__gt=search_value, server=server)
    elif search_type == 'sawmill_below':
        islands = Island.objects.all().filter(wood_level__lt=search_value, server=server)
    elif search_type == 'luxury_above':
        islands = Island.objects.all().filter(luxury_level__gt=search_value, server=server)
    elif search_type == 'luxury_below':
        islands = Island.objects.all().filter(luxury_level__lt=search_value, server=server)
    elif search_type == 'towns_above':
        islands = Island.objects.all().annotate(towns=Count('town', 0)).filter(towns__gt=search_value, server=server)
    elif search_type == 'towns_below':
        islands = Island.objects.all().annotate(towns=Count('town', 0)).filter(towns__lt=search_value, server=server)
    elif search_type == 'has_tower':
        islands = Island.objects.all().filter(has_tower=True, server=server)

    for island in islands:
        coords.append([island.x, island.y])
    return coords


def get_displayable_search_name(search_name: str):
    if not search_name:
        return ''
    names = {
        "sawmill_above": "Tartak powyżej",
        "sawmill_below": "Tartak poniżej",
        "luxury_above": "Kopalnia powyżej",
        "luxury_below": "Kopalnia poniżej",
        "towns_above": "Miasta powżej",
        "towns_below": "Miasta poniżej",
        "has_tower": "Wyspy z wieżą",
    }
    return names[search_name]


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


def get_chart_data(user_id, rank_type, selected_date):
    chart_data = []
    rows = UserHistory.objects.filter(user__id=user_id, time__range=[selected_date, datetime.today()]).order_by('time')
    for row in rows:
        points = get_points_from_rank(row, rank_type)
        if points and points > 0:
            chart_data.append([row.time, points])
    return chart_data


def get_points_from_rank(user_history, rank_type):
    if rank_type == 'score':
        return user_history.score
    elif rank_type == 'master_builders':
        return user_history.master_builders
    elif rank_type == 'building_levels':
        return user_history.building_levels
    elif rank_type == 'scientists':
        return user_history.scientists
    elif rank_type == 'research_level':
        return user_history.research_level
    elif rank_type == 'generals':
        return user_history.generals
    elif rank_type == 'gold':
        return user_history.gold
    elif rank_type == 'offensive':
        return user_history.offensive
    elif rank_type == 'defensive':
        return user_history.defensive
    elif rank_type == 'trading':
        return user_history.trading
    elif rank_type == 'resources':
        return user_history.resources
    elif rank_type == 'donations':
        return user_history.donations
    elif rank_type == 'piracy':
        return user_history.piracy


def get_towns_as_text(towns) -> str:
    text = ""
    previous_town = None
    for town in towns:
        if previous_town is not None and town.island != previous_town.island:
            text += '----------------------------------------------------------\n'
        text += f'{town.town_name} {get_island_info(town, previous_town)}\n'
        previous_town = town
    return text


def get_island_info(town, previous_town):
    if previous_town is not None and town.island == previous_town.island:
        return ""
    return f'[{town.island.x}:{town.island.y}] Tartak {town.island.wood_level.level} {town.island.luxury_resource.name} {town.island.luxury_level.level} {town.island.miracle.name}'