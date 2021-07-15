from django.db import connection
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.db.models import Count

from ..models import User, Town, Island, Resource

from .user_units import get_sum_units_points, get_sum_units_costs
from .user_ships import get_sum_ships_points, get_sum_ships_costs
from django.contrib.auth.decorators import login_required


@login_required(login_url='helper:login')
def get_user_towns(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.last_visit = datetime.now()
    user.save()

    costs_units_discount = 1.0 - user.military_future * 0.02 - 0.14
    costs_ships_discount = 1.0 - user.shipping_future * 0.02 - 0.14
    towns = Town.objects.filter(user__id=user_id).order_by('island')

    wood_workers = get_workers(user_id)
    wine_workers = get_mine_workers(user_id, 2)
    marble_workers = get_mine_workers(user_id, 3)
    crystal_workers = get_mine_workers(user_id, 4)
    sulfur_workers = get_mine_workers(user_id, 5)

    username = request.GET.get('username', '')
    alliance_tag = request.GET.get('alliance_tag', '')
    search_type = request.GET.get('search_type', '')
    search_value = request.GET.get('search_value', 0)

    context = {
        'user': user,
        'user_id': user_id,
        'username': username,
        'alliance_tag': alliance_tag,
        'search_type': search_type,
        'search_value': search_value,
        'towns': towns,
        'sum_points': int(get_sum_units_points(user_id) + get_sum_ships_points(user_id)),
        'sum_costs': int(get_sum_units_costs(user_id)*costs_units_discount +
                               get_sum_ships_costs(user_id)*costs_ships_discount),
        'wood_workers': wood_workers,
        'wine_workers': wine_workers,
        'marble_workers': marble_workers,
        'crystal_workers': crystal_workers,
        'sulfur_workers': sulfur_workers,
        'all_workers': wood_workers + wine_workers + marble_workers + crystal_workers + sulfur_workers,
        'all_islands': get_coordinates(Island.objects.all()),
        'occupied_islands': get_occupied_islands(),
        'own_islands': get_coordinates_for_towns(towns),
        'searched_islands': get_searched_coordinates(username, alliance_tag, search_type, search_value),
        'nav_active': 'user_towns',
        'title': 'Miasta - ' + user.user_name
    }
    return render(request, 'helper/user_towns.html', context)


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
                        luxury_level=1, luxury_resource=resource)
        island.save()
        return island


def delete_town(request, user_id):
    Town.objects.filter(pk=request.POST['town_id']).delete()
    return HttpResponseRedirect(reverse('helper:user_towns', args=(user_id,)))


def get_workers(user_id):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT SUM(s.workers)"
        "FROM helper_sawmillworkers AS s INNER JOIN helper_island as i ON i.wood_level == s.level INNER JOIN helper_town as t ON t.island_id == i.id WHERE t.user_id == %s"
        , [user_id])
    results = cursor.fetchall()
    if results[0][0] is None:
        return 0
    return results[0][0]


def get_mine_workers(user_id, mine_type):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT SUM(m.workers)"
        "FROM helper_mineworkers AS m INNER JOIN helper_island as i ON i.luxury_level == m.level INNER JOIN helper_town as t ON t.island_id == i.id WHERE t.user_id == %s AND i.luxury_resource_id == %s"
        , [user_id, mine_type])
    results = cursor.fetchall()
    if results[0][0] is None:
        return 0
    return results[0][0]


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
    towns = Town.objects.filter(Q(user__user_name=username))
    return get_coordinates_for_towns(towns)


def get_alliance_coords(alliance_tag):
    towns = Town.objects.filter(Q(user__alliance=alliance_tag))
    return get_coordinates_for_towns(towns)


def get_occupied_islands():
    occupied_islands = Island.objects.all().annotate(towns=Count('town')).filter(towns__gt=0)
    coords = []
    for island in occupied_islands:
        coords.append([island.x, island.y])
    return coords


def get_selected_islands(search_type, search_value):
    islands = []
    coords = []
    if search_type == 'sawmill_above':
        islands = Island.objects.all().filter(wood_level__gt=search_value)
    elif search_type == 'sawmill_below':
        islands = Island.objects.all().filter(wood_level__lt=search_value)
    elif search_type == 'luxury_above':
        islands = Island.objects.all().filter(luxury_level__gt=search_value)
    elif search_type == 'luxury_below':
        islands = Island.objects.all().filter(luxury_level__lt=search_value)
    elif search_type == 'luxury_wine':
        islands = Island.objects.all().filter(luxury_resource=2)
    elif search_type == 'luxury_marble':
        islands = Island.objects.all().filter(luxury_resource=3)
    elif search_type == 'luxury_crystal':
        islands = Island.objects.all().filter(luxury_resource=4)
    elif search_type == 'luxury_sulfur':
        islands = Island.objects.all().filter(luxury_resource=5)
    elif search_type == 'towns_above':
        islands = Island.objects.all().annotate(towns=Count('town', 0)).filter(towns__gt=search_value)
    elif search_type == 'towns_below':
        islands = Island.objects.all().annotate(towns=Count('town', 0)).filter(towns__lt=search_value)
    elif search_type == 'has_tower':
        islands = Island.objects.all().filter(has_tower=True)

    for island in islands:
        coords.append([island.x, island.y])
    return coords

