from ..models import User, TownResources, Resource
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from datetime import datetime


class UserResourcesView(generic.DetailView):
    template_name = 'helper/user_resources.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(UserResourcesView, self).get_context_data()
        user_id = context['user'].id
        context['resources'] = TownResources.objects.filter(town__user_id=user_id)
        context['resource_types'] = Resource.objects.all()
        wood = 0
        wood_production = 0
        wine = 0
        wine_production = 0
        tavern_expenses = 0
        marble = 0
        marble_production = 0
        crystal = 0
        crystal_production = 0
        sulfur = 0
        sulfur_production = 0
        for resource in context['resources']:
            update_resources(resource)
            wood += resource.wood
            wood_production += resource.wood_production
            wine += resource.wine
            wine_production += resource.wine_production
            tavern_expenses += resource.tavern_expenses
            marble += resource.marble
            marble_production += resource.marble_production
            crystal += resource.crystal
            crystal_production += resource.crystal_production
            sulfur += resource.sulfur
            sulfur_production += resource.sulfur_production
        context['sum_wood'] = wood
        context['sum_wood_production'] = wood_production
        context['sum_wine'] = wine
        context['sum_wine_production'] = wine_production
        context['sum_tavern_expenses'] = tavern_expenses
        context['sum_marble'] = marble
        context['sum_marble_production'] = marble_production
        context['sum_crystal'] = crystal
        context['sum_crystal_production'] = crystal_production
        context['sum_sulfur'] = sulfur
        context['sum_sulfur_production'] = sulfur_production

        context['nav_active'] = 'user_resources'
        context['title'] = 'Surowce - ' + context['user'].user_name
        return context


def save_resources(request, user_id):
    obj = TownResources.objects.get(pk=request.POST['id'])
    obj.wood = request.POST['wood']
    obj.wood_production = request.POST['wood_production']
    obj.wine = request.POST['wine']
    obj.wine_production = request.POST['wine_production']
    obj.marble = request.POST['marble']
    obj.marble_production = request.POST['marble_production']
    obj.crystal = request.POST['crystal']
    obj.crystal_production = request.POST['crystal_production']
    obj.sulfur = request.POST['sulfur']
    obj.sulfur_production = request.POST['sulfur_production']
    obj.tavern_expenses = request.POST['tavern_expenses']
    obj.save_time = datetime.now()
    obj.save()
    return HttpResponseRedirect(reverse('helper:user_resources', args=(user_id,)))


def update_resources(town_resources):
    time_in_hours = (datetime.now() - town_resources.save_time).total_seconds() / 3600
    town_resources.wood += int(town_resources.wood_production * time_in_hours)
    town_resources.wine += int(town_resources.wine_production * time_in_hours) - int(town_resources.tavern_expenses * time_in_hours)
    town_resources.marble += int(town_resources.marble_production * time_in_hours)
    town_resources.crystal += int(town_resources.crystal_production * time_in_hours)
    town_resources.sulfur += int(town_resources.sulfur_production * time_in_hours)
    return town_resources


def send_resources(request, user_id):
    resources_type = int(request.POST['resource_choice'])
    resources_number = int(request.POST['resources_number'])

    from_town = update_resources(TownResources.objects.get(pk=request.POST['from_town']))
    to_town = update_resources(TownResources.objects.get(pk=request.POST['to_town']))
    from_town.save_time = datetime.now()
    to_town.save_time = datetime.now()
    if resources_type == 1:
        from_town.wood -= resources_number
        to_town.wood += resources_number
    elif resources_type == 2:
        from_town.wine -= resources_number
        to_town.wine += resources_number
    elif resources_type == 3:
        from_town.marble -= resources_number
        to_town.marble += resources_number
    elif resources_type == 4:
        from_town.crystal -= resources_number
        to_town.crystal += resources_number
    elif resources_type == 5:
        from_town.sulfur -= resources_number
        to_town.sulfur += resources_number

    from_town.save()
    to_town.save()
    return HttpResponseRedirect(reverse('helper:user_resources', args=(user_id,)))


def add_all(request, user_id):
    resources = TownResources.objects.filter(town__user_id=user_id)
    increase_value = int(request.POST['increase_all'])
    for resource in resources:
        resource.wood += increase_value
        resource.wine += increase_value
        resource.marble += increase_value
        resource.crystal += increase_value
        resource.sulfur += increase_value
        resource.save()
    return HttpResponseRedirect(reverse('helper:user_resources', args=(user_id,)))
