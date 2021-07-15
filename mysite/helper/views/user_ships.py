from ..models import User, Ship, ShipInstance, Town
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.db import connection
from django.contrib.auth.decorators import login_required


class UserShipsView(generic.DetailView):
    template_name = 'helper/user_ships.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(UserShipsView, self).get_context_data()
        user_id = context['user'].id
        context['ships'] = Ship.objects.all()
        context['towns'] = Town.objects.filter(user__id=user_id)

        ship_instances = self.get_ship_instances(context['towns'])
        context['ships_instances'] = zip(ship_instances[0], ship_instances[1])
        costs_discount = 1.0 - context['user'].shipping_future*0.02 - 0.14
        sum_ships = []
        costs = []
        points = []
        sum_costs = 0
        with connection.cursor() as cursor:
            for a in cursor.execute(
                "SELECT SUM(si.number), s.hour_costs as sso, s.points as wwo FROM helper_shipinstance AS si INNER JOIN helper_ship as s ON si.ship_id == s.id INNER JOIN helper_town as t ON si.town_id == t.id WHERE t.user_id == %s GROUP BY si.ship_id",
                    [user_id]):
                sum_ships.append(a[0])
                cost = a[0]*a[1]*costs_discount
                costs.append(int(cost))
                points.append(int(a[0] * a[2]))
                sum_costs += cost
        context['sum_ships'] = sum_ships
        context['costs'] = costs
        context['points'] = points
        context['sum_costs'] = int(sum_costs)
        context['sum_points'] = int(get_sum_ships_points(user_id))

        context['nav_active'] = 'user_ships'
        context['title'] = 'Statki - ' + context['user'].user_name
        return context

    def get_ship_instances(self, towns):
        ship_instances = [], []
        for i in range(len(towns)):
            ships_in_town = ShipInstance.objects.filter(town=towns[i])
            ship_instances[0].append(ships_in_town)
            ship_instances[1].append(towns[i].no_ships)
        return ship_instances


def get_sum_ships_points(user_id):
    cursor = connection.cursor()
    cursor.execute(
            "SELECT SUM(si.number * s.points)"
            "FROM helper_shipinstance AS si "
            "INNER JOIN helper_ship as s ON si.ship_id == s.id "
            "INNER JOIN helper_town as t ON si.town_id == t.id "
            "WHERE t.user_id == %s  ", [user_id])
    results = cursor.fetchall()
    if results[0][0] is None:
        return 0
    return results[0][0]


def get_sum_ships_costs(user_id):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT SUM(si.number * s.hour_costs)"
        "FROM helper_shipinstance AS si "
        "INNER JOIN helper_ship as s ON si.ship_id == s.id "
        "INNER JOIN helper_town as t ON si.town_id == t.id "
        "WHERE t.user_id == %s  ", [user_id])
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
    return HttpResponseRedirect(reverse('helper:user_ships', args=(user_id,)))


def toggle_no_ships(request, user_id):
    town_id = request.POST['town_id']
    town = Town.objects.get(pk=town_id)
    town.no_ships = not town.no_ships
    town.save()
    return HttpResponseRedirect(reverse('helper:user_ships', args=(user_id,)))
