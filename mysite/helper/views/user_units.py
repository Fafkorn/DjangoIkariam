from ..models import User, Unit, UnitInstance, Town
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.db import connection
from django.contrib.auth.decorators import login_required


class UserUnitsView(generic.DetailView):
    template_name = 'helper/user_units.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(UserUnitsView, self).get_context_data()
        user_id = context['user'].id
        context['units'] = Unit.objects.all()
        context['towns'] = Town.objects.filter(user__id=user_id)

        unit_instances = self.get_unit_instances(context['towns'])
        context['units_instances'] = zip(unit_instances[0], unit_instances[1])

        sum_units = []
        costs = []
        points = []
        sum_costs = 0
        discount = 1.0 - context['user'].military_future*0.02 - 0.14
        with connection.cursor() as cursor:
            for a in cursor.execute(
                "SELECT SUM(ui.number), u.hour_costs as sso, u.points as wwo "
                "FROM helper_unitinstance AS ui "
                "INNER JOIN helper_unit as u ON ui.unit_id == u.id "
                "INNER JOIN helper_town as t ON ui.town_id == t.id "
                "WHERE t.user_id == %s  "
                "GROUP BY ui.unit_id",
                    [user_id]):
                sum_units.append(a[0])
                cost = a[0] * a[1] * discount
                costs.append(int(cost))
                points.append(int(a[0] * a[2]))
                sum_costs += cost
        context['sum_units'] = sum_units
        context['costs'] = costs
        context['points'] = points
        context['sum_costs'] = int(sum_costs)
        context['sum_points'] = int(get_sum_units_points(user_id))

        context['nav_active'] = 'user_units'
        context['title'] = 'Jednostki - ' + context['user'].user_name
        return context

    def get_unit_instances(self, towns):
        unit_instances = [[], []]
        for i in range(len(towns)):
            units_in_town = UnitInstance.objects.filter(town=towns[i])
            unit_instances[0].append(units_in_town)
            unit_instances[1].append(towns[i].no_units)
        return unit_instances


def get_sum_units_points(user_id):
    cursor = connection.cursor()
    cursor.execute(
            "SELECT SUM(ui.number * u.points)"
            "FROM helper_unitinstance AS ui "
            "INNER JOIN helper_unit as u ON ui.unit_id == u.id "
            "INNER JOIN helper_town as t ON ui.town_id == t.id "
            "WHERE t.user_id == %s  ", [user_id])
    results = cursor.fetchall()
    if results[0][0] is None:
        return 0
    return results[0][0]


def get_sum_units_costs(user_id):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT SUM(ui.number * u.hour_costs)"
        "FROM helper_unitinstance AS ui "
        "INNER JOIN helper_unit as u ON ui.unit_id == u.id "
        "INNER JOIN helper_town as t ON ui.town_id == t.id "
        "WHERE t.user_id == %s  ", [user_id])
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
    return HttpResponseRedirect(reverse('helper:user_units', args=(user_id,)))


def toggle_no_units(request, user_id):
    town_id = request.POST['town_id']
    town = Town.objects.get(pk=town_id)
    town.no_units = not town.no_units
    town.save()
    return HttpResponseRedirect(reverse('helper:user_units', args=(user_id,)))
