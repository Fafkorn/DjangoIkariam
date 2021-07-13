import requests
import time
from django.shortcuts import render
import json
from django.http import HttpResponseRedirect
from django.urls import reverse
from ..models import User, Town, Resource, Miracle, Island, Building, BuildingInstance, UserStatus
from bs4 import BeautifulSoup


def admin_site(request):
    context = {'title': 'Admin'}
    return render(request, 'helper/admin.html', context)


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


def web_scrap_all_islands(request):
    cookie = request.POST['cookie']
    password = request.POST['password']
    if not str(password) == '1234':
        return HttpResponseRedirect(reverse('helper:admin', args=()))
    else:
        print('Hasło poprawne')
    print(str(cookie))
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        #  TODO edit Cookie
        "Cookie": str(cookie),
        "Host": "s6-pl.ikariam.gameforge.com",
        "Referer": "https://s6-pl.ikariam.gameforge.com/?view=worldmap_iso&oldBackgroundView=island&containerWidth=1903px&containerHeight=600px&worldviewWidth=1903px&worldviewHeight=554px&islandTop=-687px&islandLeft=-1838px&islandRight=&islandWorldviewScale=1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    }
    for i in range(9999):
        url = 'https://s6-pl.ikariam.gameforge.com/?view=island&islandId=' + str(i+0)
        print(url)
        time.sleep(2)
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        scripts = soup.find_all("script", {"type": "text/javascript"})
        convert_island_script_to_data(scripts)
    return HttpResponseRedirect(reverse('helper:admin', args=()))


def web_scrap_island(request):
    text = request.POST['textarea']
    soup = BeautifulSoup(text, 'html.parser')
    scripts = soup.find_all("script", {"type": "text/javascript"})
    convert_island_script_to_data(scripts)
    return HttpResponseRedirect(reverse('helper:admin', args=()))


def convert_island_script_to_data(scripts):
    for script in scripts:
        if "$(document).ready(function () {" in str(script) and "xCoord" in str(script):
            script_string = str(script).strip()
            start = script_string.find("[")
            last = script_string.rfind("]")
            script_string = script_string[start:last+1]
            json_object = json.loads(script_string)
            x = json_object[0][1]['xCoord']
            y = json_object[0][1]['yCoord']

            island = get_island(x, y)
            island.name = json_object[0][1]['name']
            island.wood_level = json_object[0][1]['resourceLevel']
            island.luxury_resource = Resource.objects.get(pk=int(json_object[0][1]['tradegood'])+1)
            island.luxury_level = json_object[0][1]['tradegoodLevel']
            island.miracle = Miracle.objects.get(pk=json_object[0][1]['wonder'])
            island.miracle_level = json_object[0][1]['wonderLevel']
            island.has_tower = json_object[0][1]['isHeliosTowerBuilt']
            island.save()
            cities = json_object[0][1]['cities']

            towns_to_save = []
            for city in cities:
                if not (city['id'] == -1):
                    owner_ally_tag = ''
                    if 'ownerAllyTag' in city:
                        owner_ally_tag = city['ownerAllyTag']
                    user = get_user(city['ownerName'], owner_ally_tag)
                    town = get_town(city['name'], user, island, city['id'])
                    if town is not None:
                        towns_to_save.append(town)
                        print(town.town_name + ' added')
            Town.objects.bulk_create(towns_to_save)

            towns_database = Town.objects.filter(island__id=island.id)
            delete_missing_towns(cities, towns_database)


def delete_missing_towns(towns_script, towns_database):
    towns_script_ids = []
    for city in towns_script:
        if city['id'] != -1:
            towns_script_ids.append(city['id'])

    for town in towns_database:
        if town.in_game_id not in towns_script_ids:
            print('Town id=' + str(town.in_game_id) + ' - DELETED')
            town.delete()


def web_scrap(request):
    titles = ['Pan Cieni', 'Imperator', 'Mistrz Sztuk Pięknych', 'Geniusz', 'Korsarz', 'Ambasador', 'Mecenas',
              'Bicz Barbarzyńców', 'Najwyższy Namiestnik', 'Strażnik Wiedzy', 'Hurtownik', 'Syzyf', 'Burmistrz',
              'Maratończyk', 'Łatacz Żagli', 'Cudowne Dziecko', 'Pan Kopalni Kryształu', 'Szczur Laboratoryjny',
              'Gubernator', 'Kolekcjoner punktów', 'Postrach Oceanów', 'Ulubieniec Apollona', 'Admirał',
              'Supermózg', 'Miłośnik Sztuki', 'Szpieg', 'Pan Winorośli', 'Skarbnik Króla Midasa',
              'Pan Kopalni Siarki', 'Pan Tartaków', 'Reformator', 'Kapitan Piratów', 'Pogromca Herkulesa',
              'Duma Hermesa', 'Szef Kuchni', 'Król Handlarzy Bronią']
    text = request.POST['textarea']
    soup = BeautifulSoup(text, 'html.parser')

    option_list = soup.find_all("span", {"class": "dropDownButton"})
    option = option_list[1].text

    names = []
    statuses = []
    td_name = soup.find_all("td", {"class": "name"})
    print(td_name)
    for element in td_name:
        name = element.text
        statuses.append(get_status(element))
        print(f"{name.strip()} {get_status(element)}")
        for title in titles:
            name = name.replace(title, '')
        names.append(name.strip())

    allies = []
    td_ally = soup.find_all("td", {"class": "allytag"})
    for element in td_ally:
        allies.append(element.text.replace('\n', ''))

    scores = []
    td_score = soup.find_all("td", {"class": "score"})
    for element in td_score:
        scores.append(element.text.replace(',', ''))

    data = zip(names, allies, scores, statuses)
    for entry in data:
        user = User.objects.filter(user_name=entry[0])
        if user:
            user = user[0]
            user.alliance = entry[1]
            # user[0].save()
        else:
            user = User(user_name=entry[0], alliance=entry[1])
            # user.save()

        if 'Całkowity wynik' in option:
            user.score = entry[2]
        elif 'Mistrzowie budowy' in option:
            user.master_builders = entry[2]
        elif 'Poziomy budynków' in option:
            user.building_levels = entry[2]
        elif 'Naukowcy' in option:
            user.scientists = entry[2]
        elif 'Poziomy badań' in option:
            user.research_level = entry[2]
        elif 'Generałowie' in option:
            user.generals = entry[2]
        elif 'Zapas złota' in option:
            user.gold = entry[2]
        elif 'Punkty ofensywy' in option:
            user.offensive = entry[2]
        elif 'Punkty obrony' in option:
            user.defensive = entry[2]
        elif 'Handlarz' in option:
            user.trading = entry[2]
        elif 'Surowce' in option:
            user.resources = entry[2]
        elif 'Datki' in option:
            user.donations = entry[2]
        elif 'Punkty Abordażu' in option:
            user.piracy = entry[2]

        user.user_status = UserStatus.objects.get(pk=entry[3])
        user.save()

    return HttpResponseRedirect(reverse('helper:admin', args=()))


def get_status(element):
    if element.find('a').get('class') and 'gray' in element.find('a').get('class'):
        return 2
    elif element.find('img'):
        return 4
    else:
        return 1


def web_scrap_town(request):
    text = request.POST['textarea']
    soup = BeautifulSoup(text, 'html.parser')
    scripts = soup.find_all("script", {"type": "text/javascript"})
    convert_town_script_to_data(scripts)
    return HttpResponseRedirect(reverse('helper:admin', args=()))


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


def set_all_users_deleted(request):
    User.objects.update(user_status=3)
    return HttpResponseRedirect(reverse('helper:admin', args=()))
