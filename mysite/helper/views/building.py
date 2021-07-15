from django.urls import reverse

from ..models import BuildingInstance, User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required


class BuildingView(generic.DetailView):
    template_name = 'helper/building.html'
    model = BuildingInstance

    def get_context_data(self, **kwargs):
        context = super(BuildingView, self).get_context_data()
        context['user'] = get_object_or_404(User, pk=context['buildinginstance'].building_town.user.id)
        context['nav_active'] = 'user_buildings'
        context['title'] = context['buildinginstance'].building_type.building_name + ' - ' + context['buildinginstance'].building_town.town_name
        return context


def update_building(request, instance_building_id):
    building_instance = get_object_or_404(BuildingInstance, pk=instance_building_id)
    building_instance.level = request.POST['level']
    building_instance.save()
    return HttpResponseRedirect(reverse('helper:building', args=(building_instance.id,)))


def start_develop_building(request, instance_building_id):
    building_instance = get_object_or_404(BuildingInstance, pk=instance_building_id)
    building_instance.is_upgraded = True
    building_instance.save()
    return HttpResponseRedirect(reverse('helper:building', args=(building_instance.id,)))


def stop_develop_building(request, instance_building_id):
    building_instance = get_object_or_404(BuildingInstance, pk=instance_building_id)
    building_instance.is_upgraded = False
    building_instance.save()
    return HttpResponseRedirect(reverse('helper:building', args=(building_instance.id,)))