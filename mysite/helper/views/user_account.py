from django.http import HttpResponseRedirect
from django.urls import reverse

from ..models import User, Town, Island, Resource, BuildingInstance, SawMillWorkers, MineWorkers
from django.views import generic

from .user_units import get_sum_units_points, get_sum_units_costs
from .user_ships import get_sum_ships_points, get_sum_ships_costs


class UserAccountView(generic.DetailView):
    template_name = 'helper/user_account.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(UserAccountView, self).get_context_data()
        user_id = context['user'].id
        costs_units_discount = 1.0 - context['user'].military_future * 0.02 - 0.14
        costs_ships_discount = 1.0 - context['user'].shipping_future * 0.02 - 0.14
        context['towns'] = Town.objects.filter(user__id=user_id).order_by('island')
        context['sum_points'] = int(get_sum_units_points(user_id) + get_sum_ships_points(user_id))
        context['sum_costs'] = int(get_sum_units_costs(user_id)*costs_units_discount +
                                   get_sum_ships_costs(user_id)*costs_ships_discount)
        context['nav_active'] = 'user_account'
        context['title'] = 'Konto - ' + context['user'].user_name
        return context


def add_town(request, user_id):
    island = get_island(request.POST['x'], request.POST['y'])
    new_town = Town(user_id=user_id,
                    town_name=request.POST['town_name'],
                    island=island)
    new_town.save()
    return HttpResponseRedirect(reverse('helper:user_account', args=(user_id,)))


def update_town(request, user_id):
    town = Town.objects.get(pk=request.POST['town_id'])
    island = get_island(request.POST['town_x'], request.POST['town_y'])
    town.town_name = request.POST['town_name']
    town.island = island
    town.save()
    return HttpResponseRedirect(reverse('helper:user_account', args=(user_id,)))


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


def enable_towns(request, user_id):
    user_towns = Town.objects.filter(user__id=user_id)
    for town in user_towns:
        if len(BuildingInstance.objects.filter(building_town__id=town.id)) == 0:
            town.create_related_objects()
    return HttpResponseRedirect(reverse('helper:user_account', args=(user_id,)))


def delete_town(request, user_id):
    Town.objects.filter(pk=request.POST['town_id']).delete()
    return HttpResponseRedirect(reverse('helper:user_account', args=(user_id,)))


def save_researches(request, user_id):
    user = User.objects.get(pk=user_id)
    user.shipping_future = request.POST['shipping_future']
    user.economy_future = request.POST['economy_future']
    user.science_future = request.POST['science_future']
    user.military_future = request.POST['military_future']
    user.save()
    return HttpResponseRedirect(reverse('helper:user_account', args=(user_id,)))


def edit_user_name(request, user_id):
    user_name = request.POST['user_name']
    user = User.objects.get(pk=user_id)
    user.user_name = user_name
    user.save()
    return HttpResponseRedirect(reverse('helper:user_account', args=(user_id,)))


def delete_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return HttpResponseRedirect(reverse('helper:users', args=()))

