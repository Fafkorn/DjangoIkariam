from django.shortcuts import render

from ..models import User, Unit, Ship, UnitInstance, ShipInstance, Town
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import connection
from django.contrib.auth.decorators import login_required


@login_required(login_url='helper:login')
def get_user_army(request, user_id):
    context = {}
    context['ships'] = Ship.objects.all()
    context['units'] = Unit.objects.all()
    context['towns'] = Town.objects.filter(user__id=user_id)

    context['user'] = User.objects.get(pk=user_id)

    unit_instances = get_unit_instances(context['towns'])
    context['units_instances'] = zip(unit_instances[0], unit_instances[1])

    sum_units = []
    units_costs = []
    units_points = []
    sum_costs = 0
    discount = 1.0 - context['user'].military_future*0.02 - 0.14
    with connection.cursor() as cursor:
        for a in cursor.execute(
            "SELECT SUM(ui.number), u.hour_costs as sso, u.points as wwo FROM helper_unitinstance AS ui INNER JOIN helper_unit as u ON ui.unit_id = u.id INNER JOIN helper_town as t ON ui.town_id = t.id WHERE t.user_id = %s GROUP BY ui.unit_id, u.hour_costs",
                [user_id]):
            sum_units.append(a[0])
            cost = a[0] * a[1] * discount
            units_costs.append(int(cost))
            units_points.append(int(a[0] * a[2]))
            sum_costs += cost
    context['sum_units'] = sum_units
    context['units_costs'] = units_costs
    context['units_points'] = units_points
    context['sum_units_costs'] = int(sum_costs)
    context['sum_units_points'] = int(get_sum_units_points(user_id))

    ship_instances = get_ship_instances(context['towns'])
    context['ships_instances'] = zip(ship_instances[0], ship_instances[1])
    costs_discount = 1.0 - context['user'].shipping_future * 0.02 - 0.14
    sum_ships = []
    ships_costs = []
    ships_points = []
    sum_costs = 0
    with connection.cursor() as cursor:
        for a in cursor.execute(
                "SELECT SUM(si.number), s.hour_costs as sso, s.points as wwo FROM helper_shipinstance AS si INNER JOIN helper_ship as s ON si.ship_id = s.id INNER JOIN helper_town as t ON si.town_id = t.id WHERE t.user_id = %s GROUP BY si.ship_id, s.hour_costs",
                [user_id]):
            sum_ships.append(a[0])
            cost = a[0] * a[1] * costs_discount
            ships_costs.append(int(cost))
            ships_points.append(int(a[0] * a[2]))
            sum_costs += cost
    context['sum_ships'] = sum_ships
    context['ships_costs'] = ships_costs
    context['ships_points'] = ships_points
    context['sum_ships_costs'] = int(sum_costs)
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
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(ui.number * u.points) FROM helper_unitinstance AS ui INNER JOIN helper_unit as u ON ui.unit_id = u.id INNER JOIN helper_town as t ON ui.town_id = t.id WHERE t.user_id = %s  ", [user_id])
    results = cursor.fetchall()
    if results[0][0] is None:
        return 0
    return results[0][0]


def get_sum_units_costs(user_id):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT SUM(ui.number * u.hour_costs) FROM helper_unitinstance AS ui INNER JOIN helper_unit as u ON ui.unit_id = u.id INNER JOIN helper_town as t ON ui.town_id = t.id WHERE t.user_id = %s  ", [user_id])
    results = cursor.fetchall()
    if results[0][0] is None:
        return 0
    return results[0][0]


def save_units(request, user_id):
    unit_ids = request.POST.getlist('unit_id')
    numbers = request.POST.getlist('unit_number')
    for i, unit_id in enumerate(unit_ids):
        unit_instance = UnitInstance.objects.get(pk=unit_id)
        if unit_instance.number != numbers[i]:
            unit_instance.number = numbers[i]
            unit_instance.save()
    return HttpResponseRedirect(reverse('helper:user_army', args=(user_id,)))


def toggle_no_units(request, user_id):
    town_id = request.POST['town_id']
    town = Town.objects.get(pk=town_id)
    town.no_units = not town.no_units
    town.save()
    return HttpResponseRedirect(reverse('helper:user_army', args=(user_id,)))


def get_sum_ships_points(user_id):
    cursor = connection.cursor()
    cursor.execute(
            "SELECT SUM(si.number * s.points) FROM helper_shipinstance AS si INNER JOIN helper_ship as s ON si.ship_id = s.id INNER JOIN helper_town as t ON si.town_id = t.id  WHERE t.user_id = %s  ", [user_id])
    results = cursor.fetchall()
    if results[0][0] is None:
        return 0
    return results[0][0]


def get_sum_ships_costs(user_id):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT SUM(si.number * s.hour_costs) FROM helper_shipinstance AS si INNER JOIN helper_ship as s ON si.ship_id = s.id INNER JOIN helper_town as t ON si.town_id = t.id WHERE t.user_id = %s  ", [user_id])
    results = cursor.fetchall()
    if results[0][0] is None:
        return 0
    return results[0][0]


def save_ships(request, user_id):
    ship_ids = request.POST.getlist('ship_id')
    numbers = request.POST.getlist('ship_number')
    for i, unit_id in enumerate(ship_ids):
        ship_instance = ShipInstance.objects.get(pk=unit_id)
        if ship_instance.number != numbers[i]:
            ship_instance.number = numbers[i]
            ship_instance.save()
    return HttpResponseRedirect(reverse('helper:user_army', args=(user_id,)))


def toggle_no_ships(request, user_id):
    town_id = request.POST['town_id']
    town = Town.objects.get(pk=town_id)
    town.no_ships = not town.no_ships
    town.save()
    return HttpResponseRedirect(reverse('helper:user_army', args=(user_id,)))
