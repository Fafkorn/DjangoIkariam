from django.http import HttpResponseRedirect
from django.urls import reverse

from ..models import User, Building, BuildingInstance, Town
from django.views import generic


class UserBuildingsView(generic.DetailView):
    template_name = 'helper/user_buildings.html'
    model = User
    player_to_compare = None

    def get_context_data(self, **kwargs):
        context = super(UserBuildingsView, self).get_context_data()
        user_id = context['user'].id
        context['buildings'] = Building.objects.order_by('order')
        context['towns'] = Town.objects.filter(user__id=user_id)
        context['building_instances'] = self.get_building_instances(context['towns'], context)
        context['nav_active'] = 'user_buildings'
        context['title'] = 'Budynki - ' + context['user'].user_name
        return context

    def get_building_instances(self, towns, context):
        building_instances = []
        level_sum = 0
        for i in range(len(towns)):
            buildings_in_town = BuildingInstance.objects.filter(building_town=towns[i]).order_by('building_type__order')
            building_instances.append(buildings_in_town)
            for building in buildings_in_town:
                level_sum += building.level
        context['level_sum'] = level_sum
        return building_instances

    def compare_with_player(self, request):
        text = request.POST['textarea']
        print(text)
        self.player_to_compare = 2
        return HttpResponseRedirect(reverse('helper:user_buildings', args=()))
