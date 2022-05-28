from django.db.models import F, Sum
from django.shortcuts import render

from ..models import User, Unit, Ship, UnitInstance, ShipInstance, Town
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from mysite import settings

server = settings.ACTIVE_SERVER


@login_required(login_url='helper:login')
def get_user_army(request, user_id):
    context = {}
    context['ships'] = Ship.objects.all()
    context['units'] = Unit.objects.all()
    context['towns'] = Town.objects.filter(user__id=user_id, island__server=server).order_by('in_game_id')

    context['user'] = User.objects.get(pk=user_id)

    unit_instances = get_unit_instances(context['towns'])
    context['units_instances'] = zip(unit_instances[0], unit_instances[1])

    sum_units = []
    units_costs = []
    units_points = []
    units_discount = 1.0 - context['user'].military_future*0.02 - 0.14
    unit_types = Unit.objects.all()
    for unit in unit_types:
        unit_instances2 = UnitInstance.objects.filter(town__user__id=user_id, unit_id=unit.id, town__island__server=server)
        liczba_jednostek = 0
        koszty_jednostek = 0
        punkty_jednostek = 0
        for a in unit_instances2:
            liczba_jednostek += a.number
            koszty_jednostek += (a.number * a.unit.hour_costs) * units_discount
            punkty_jednostek += a.number * a.unit.points
        sum_units.append(liczba_jednostek)
        units_costs.append(int(koszty_jednostek))
        units_points.append(int(punkty_jednostek))

    context['sum_units'] = sum_units
    context['units_costs'] = units_costs
    context['units_points'] = units_points
    context['sum_units_costs'] = int(get_sum_units_costs(user_id) * units_discount)
    context['sum_units_points'] = int(get_sum_units_points(user_id))

    ship_instances = get_ship_instances(context['towns'])
    context['ships_instances'] = zip(ship_instances[0], ship_instances[1])
    sum_ships = []
    ships_costs = []
    ships_points = []
    ships_discount = 1.0 - context['user'].shipping_future * 0.02 - 0.14
    ship_types = Ship.objects.all()
    for ship in ship_types:
        ship_instances2 = ShipInstance.objects.filter(town__user__id=user_id, ship_id=ship.id, town__island__server=server)
        liczba_statkow = 0
        koszty_statkow = 0
        punkty_statkow = 0
        for a in ship_instances2:
            liczba_statkow += a.number
            koszty_statkow += (a.number * a.ship.hour_costs) * ships_discount
            punkty_statkow += a.number * a.ship.points
        sum_ships.append(liczba_statkow)
        ships_costs.append(int(koszty_statkow))
        ships_points.append(int(punkty_statkow))
    context['sum_ships'] = sum_ships
    context['ships_costs'] = ships_costs
    context['ships_points'] = ships_points
    context['sum_ships_costs'] = int(get_sum_ships_costs(user_id) * ships_discount)
    context['sum_ships_points'] = int(get_sum_ships_points(user_id))

    context['nav_active'] = 'user_army'
    context['title'] = 'Jednostki - ' + context['user'].user_name
    return render(request, 'helper/user_army.html', context)


def get_unit_instances(towns):
    unit_instances = [[], []]
    for i in range(len(towns)):
        units_in_town = UnitInstance.objects.filter(town=towns[i])
        unit_instances[0].append(units_in_town)
        unit_instances[1].append(towns[i].no_units)
    return unit_instances


def get_ship_instances(towns):
    ship_instances = [], []
    for i in range(len(towns)):
        ships_in_town = ShipInstance.objects.filter(town=towns[i])
        ship_instances[0].append(ships_in_town)
        ship_instances[1].append(towns[i].no_ships)
    return ship_instances


def get_sum_units_points(user_id):
    return int((UnitInstance.objects
                .filter(town__user__id=user_id, town__island__server=server)
                .annotate(points_sum=F('unit__points')*F('number'))
                .aggregate(Sum('points_sum'))['points_sum__sum']) or 0)


def get_sum_units_costs(user_id):
    return int((UnitInstance.objects
                .filter(town__user__id=user_id, town__island__server=server)
                .annotate(costs_sum=F('unit__hour_costs') * F('number'))
                .aggregate(Sum('costs_sum'))['costs_sum__sum']) or 0)


def save_units(request, user_id):
    units_to_update = []
    unit_ids = request.POST.getlist('unit_id')
    numbers = request.POST.getlist('unit_number')
    for i, unit_id in enumerate(unit_ids):
        unit_instance = UnitInstance.objects.get(pk=unit_id)
        if unit_instance.number != numbers[i]:
            try:
                int(numbers[i])
            except ValueError:
                numbers[i] = 0
            unit_instance.number = numbers[i]
            units_to_update.append(unit_instance)
    UnitInstance.objects.bulk_update(units_to_update, ['number'])
    return HttpResponseRedirect(reverse('helper:user_army', args=(user_id,)))


def toggle_no_units(request, user_id):
    town_id = request.POST['town_id']
    town = Town.objects.get(pk=town_id)
    town.no_units = not town.no_units
    town.save()
    return HttpResponseRedirect(reverse('helper:user_army', args=(user_id,)))


def get_sum_ships_points(user_id):
    return int((ShipInstance.objects
                .filter(town__user__id=user_id, town__island__server=server)
                .annotate(points_sum=F('ship__points')*F('number'))
                .aggregate(Sum('points_sum'))['points_sum__sum']) or 0)


def get_sum_ships_costs(user_id):
    return int((ShipInstance.objects
                .filter(town__user__id=user_id, town__island__server=server)
                .annotate(costs_sum=F('ship__hour_costs') * F('number'))
                .aggregate(Sum('costs_sum'))['costs_sum__sum']) or 0)


def save_ships(request, user_id):
    ships_to_update = []
    ship_ids = request.POST.getlist('ship_id')
    numbers = request.POST.getlist('ship_number')
    for i, unit_id in enumerate(ship_ids):
        ship_instance = ShipInstance.objects.get(pk=unit_id)
        if ship_instance.number != numbers[i]:
            try:
                int(numbers[i])
            except ValueError:
                numbers[i] = 0
            ship_instance.number = numbers[i]
            ships_to_update.append(ship_instance)
    ShipInstance.objects.bulk_update(ships_to_update, ['number'])
    return HttpResponseRedirect(reverse('helper:user_army', args=(user_id,)))


def toggle_no_ships(request, user_id):
    town_id = request.POST['town_id']
    town = Town.objects.get(pk=town_id)
    town.no_ships = not town.no_ships
    town.save()
    return HttpResponseRedirect(reverse('helper:user_army', args=(user_id,)))
