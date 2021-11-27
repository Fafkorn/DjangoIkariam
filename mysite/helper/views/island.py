from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from ..models import Island, User, Town, Miracle, Resource, SawMillWorkers, MineWorkers

server = "Gamma"


@login_required(login_url='helper:login')
def get_island(request, user_id, island_id):
    context = {}
    context['user'] = get_object_or_404(User, pk=user_id)
    island = Island.objects.get(pk=island_id)
    context['towns'] = Town.objects.filter(island__id=island_id).exclude(user__user_status__id=3).order_by('user')
    context['miracle_types'] = Miracle.objects.all()
    context['island'] = island
    context['next_level_saw_mill_cost'] = SawMillWorkers.objects.get(level=island.wood_level.level+1).cost
    context['next_level_mine_cost'] = MineWorkers.objects.get(level=island.luxury_level.level+1).cost
    context['title'] = f'{island.name} [{island.x}:{island.y}]'
    return render(request, 'helper/island.html', context)


def edit_island(request):
    user_id = request.POST['user_id']
    island_id = request.POST['island_id']
    island = Island.objects.get(pk=island_id)

    wood_level = SawMillWorkers.objects.filter(level=request.POST['wood_level']).first()
    island.wood_level = wood_level

    island.luxury_resource = Resource.objects.get(pk=request.POST['luxury_resource'])

    luxury_level = MineWorkers.objects.filter(level=request.POST['luxury_level']).first()
    island.luxury_level = luxury_level

    island.miracle = Miracle.objects.get(pk=request.POST['miracle_type'])
    island.miracle_level = request.POST['miracle_level']
    island.has_tower = request.POST['has_tower']
    island.save()
    return HttpResponseRedirect(reverse('helper:island', args=(user_id, island_id)))


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

