from bs4 import BeautifulSoup

import json
from mysite.helper.models import BuildingInstance, User, Building, Resource, Island, Town


def web_scrap_town(request):
    text = request.POST['html']
    soup = BeautifulSoup(text, 'html.parser')
    scripts = soup.find_all("script", {"type": "text/javascript"})
    convert_town_script_to_data(scripts)


def convert_town_script_to_data(scripts):
    for script in scripts:
        if "$(document).ready(function () {" in str(script) and "Ratusz" in str(script):
            script_string = str(script).strip()
            start = script_string.find("[")
            last = script_string.rfind("]")
            script_string = script_string[start:last+1]
            json_object = json.loads(script_string)

            x = json_object[0][1]['islandXCoord']
            y = json_object[0][1]['islandYCoord']
            city_id = json_object[0][1]['id']
            island = get_island(x, y)
            island.save()
            alliance = ""
            if 'alliance' in json_object[0][1]:
                alliance = json_object[0][1]['alliance']
            user = get_user(json_object[0][1]['ownerName'], alliance)
            town = get_town(json_object[0][1]['name'], user, island, city_id)

            if town is not None:
                town.save()
            else:
                town = Town.objects.filter(in_game_id=city_id)[0]

            BuildingInstance.objects.filter(building_town=town).delete()
            buildings_to_save = []
            all_buildings = get_all_building_instances(town)
            warehouses_count = 0
            trading_posts_count = 0
            buildings = json_object[0][1]['position']
            for building in buildings:
                if 'name' in building:
                    building_obj = Building.objects.filter(building_name=building['name'])
                    building_type = None
                    if building_obj.count() == 4:
                        building_type = building_obj[warehouses_count]
                        warehouses_count += 1
                    elif building_obj.count() == 2:
                        building_type = building_obj[trading_posts_count]
                        trading_posts_count += 1
                    elif building_obj is not None:
                        building_type = building_obj[0]

                    is_upgraded = 'completed' in building
                    building_instance = BuildingInstance(building_type=building_type, building_town=town,
                                                         level=building['level'], is_upgraded=is_upgraded)

                    buildings_to_save.append(building_instance)
                    all_buildings = find_first_and_delete(all_buildings, building_instance)
            BuildingInstance.objects.bulk_create(buildings_to_save)
            BuildingInstance.objects.bulk_create(all_buildings)


def get_all_building_instances(town):
    buildings_to_save = []
    building_types = Building.objects.all()
    for building_type in building_types:
        building_instance = BuildingInstance(building_type=building_type, building_town=town)
        buildings_to_save.append(building_instance)
    return buildings_to_save


def find_first_and_delete(buildings_list, building_instance):
    for building in buildings_list:
        if building.building_type == building_instance.building_type:
            buildings_list.remove(building)
    return buildings_list


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


def get_user(user_name, alliance):
    users = User.objects.filter(user_name=user_name)
    if users.count() == 1:
        if users[0].alliance != alliance:
            user_to_save = users[0]
            user_to_save.alliance = alliance
            user_to_save.save()
        return users[0]
    else:
        user = User(user_name=user_name)
        user.save()
        return user


def get_town(town_name, user, island, in_game_id):
    town = Town.objects.filter(in_game_id=in_game_id)
    if town.count() == 1:
        print("Town %s (%s) exists" % (town_name, user))
        town = town[0]
        town.town_name = town_name
        town.user = user
        town.save()
        return None
    else:
        town = Town(town_name=town_name, user=user, island=island, in_game_id=in_game_id)
        print("Town %s (%s) created" % (town_name, user))
        return town