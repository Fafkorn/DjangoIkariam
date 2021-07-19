from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from ..models import User, Building, BuildingInstance, Town


@login_required(login_url='helper:login')
def get_user_buildings(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    buildings = Building.objects.order_by('order')
    towns = Town.objects.filter(user__id=user_id)
    level_sum = get_sum_of_buildings_level(towns)
    building_instances = get_building_instances(towns)

    context = {
        'user': user,
        'buildings': buildings,
        'towns': towns,
        'level_sum': level_sum,
        'building_instances': building_instances,
        'selected_building': get_selected_building(request),
        'nav_active': 'user_buildings',
        'title': 'Budynki - ' + user.user_name
    }
    return render(request, 'helper/user_buildings.html', context)


def get_building_instances(towns):
    return [BuildingInstance.objects.filter(building_town=town).order_by('building_type__order') for town in towns]


def get_sum_of_buildings_level(towns):
    if len(towns) > 0:
        return BuildingInstance.objects.filter(building_town__user__id=towns[0].user.id).aggregate(Sum('level'))['level__sum']
    else:
        return 0


def get_selected_building(request):
    if 'selected_building' in request.GET:
        building_id = request.GET['selected_building']
        if building_id is not None:
            return BuildingInstance.objects.get(pk=building_id)
    return None


def update_building(request):
    instance_building_id = request.POST.get('building_instance_id')
    user_id = request.POST.get('user_id')
    building_instance = get_object_or_404(BuildingInstance, pk=instance_building_id)
    building_instance.level = request.POST['level']
    building_instance.save()
    return redirect(reverse('helper:user_buildings', args=[user_id]))


def start_develop_building(request):
    instance_building_id = request.POST.get('building_instance_id')
    user_id = request.POST.get('user_id')
    building_instance = BuildingInstance.objects.get(pk=instance_building_id)
    building_instance.is_upgraded = True
    building_instance.save()
    return redirect(reverse('helper:user_buildings', args=[user_id]))


def stop_develop_building(request):
    instance_building_id = request.POST.get('building_instance_id')
    user_id = request.POST.get('user_id')
    building_instance = get_object_or_404(BuildingInstance, pk=instance_building_id)
    building_instance.is_upgraded = False
    building_instance.save()
    return redirect(reverse('helper:user_buildings', args=[user_id]))
