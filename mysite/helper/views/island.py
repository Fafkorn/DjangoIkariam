from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
import re

from ..models import Island, User, Town, Miracle, Resource, SawMillWorkers, MineWorkers


class IslandView(generic.DetailView):
    template_name = 'helper/island.html'
    model = Island

    def get_context_data(self, **kwargs):
        context = super(IslandView, self).get_context_data()
        island = Island.objects.get(pk=self.kwargs['pk'])
        context['user'] = get_object_or_404(User, pk=self.kwargs['user_id'])
        context['towns'] = Town.objects.filter(island__id=self.kwargs['pk']).order_by('user')
        context['miracle_types'] = Miracle.objects.all()
        context['next_level_saw_mill_cost'] = SawMillWorkers.objects.get(level=island.wood_level+1).cost
        context['next_level_mine_cost'] = MineWorkers.objects.get(level=island.luxury_level+1).cost
        context['title'] = f'{island.name} [{island.x}:{island.y}]'
        return context


def edit_island(request):
    user_id = request.POST['user_id']
    island_id = request.POST['island_id']
    island = Island.objects.get(pk=island_id)
    island.wood_level = request.POST['wood_level']
    island.luxury_resource = Resource.objects.get(pk=request.POST['luxury_resource'])
    island.luxury_level = request.POST['luxury_level']
    island.miracle = Miracle.objects.get(pk=request.POST['miracle_type'])
    island.miracle_level = request.POST['miracle_level']
    island.has_tower = request.POST['has_tower']
    island.save()
    return HttpResponseRedirect(reverse('helper:island', args=(island_id, user_id)))


def delete_island(request):
    island = Island.objects.get(pk=request.POST['island_id'])
    island.delete()
    return HttpResponseRedirect(reverse('helper:user_account', args=(request.POST['user_id'],)))


def add_town(request):
    user_id = request.POST['user_id']
    island_id = request.POST['island_id']
    island = Island.objects.get(pk=island_id)
    user_name = request.POST['user_name']
    town_name = request.POST['town_name']
    user = User.objects.filter(user_name=user_name)[0]
    town = Town(town_name=town_name, user=user, island=island)
    town.save()
    return HttpResponseRedirect(reverse('helper:island', args=(island_id, user_id)))

