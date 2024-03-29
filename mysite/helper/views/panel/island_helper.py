from audioop import reverse

from bs4 import BeautifulSoup
import json

from django.contrib.sites import requests
from django.http import HttpResponseRedirect

from mysite import settings
from mysite.helper.models import User, Town, Island, Resource, Miracle, SawMillWorkers, MineWorkers, Alliance, \
    UserStatus
import time

server = settings.ACTIVE_SERVER


def web_scrap_island(request):
    text = request.POST['textarea']
    soup = BeautifulSoup(text, 'html.parser')
    scripts = soup.find_all("script", {"type": "text/javascript"})
    convert_island_script_to_data(scripts)


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
            island.wood_level = SawMillWorkers.objects.filter(level=json_object[0][1]['resourceLevel'])[0]
            island.luxury_resource = Resource.objects.get(pk=int(json_object[0][1]['tradegood'])+1)
            island.luxury_level = MineWorkers.objects.filter(level=json_object[0][1]['tradegoodLevel'])[0]
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
                    user = get_user(city['ownerName'], owner_ally_tag, city['ownerId'], city['state'])
                    town = get_town(city['name'], user, island, city['id'], city['level'])
                    if town is not None:
                        towns_to_save.append(town)
            Town.objects.bulk_create(towns_to_save)

            towns_database = Town.objects.filter(island__id=island.id, is_deleted=False)
            delete_missing_towns(cities, towns_database)


def get_island(x, y):
    island = Island.objects.filter(x=x, y=y, server=server)
    resource = Resource.objects.get(pk=1)
    if island.count() == 1:
        return island[0]
    else:
        island = Island(x=x, y=y, wood_resource=resource, luxury_resource=resource)
        island.save()
        return island


def get_user(user_name, alliance, owner_id, state):
    users = User.objects.filter(user_name=user_name, server=server)
    if users.count() > 0:
        user_to_save = users[0]
        if user_to_save.alliance != alliance:
            user_to_save.alliance = get_alliance(alliance)
        user_to_save.in_game_id = owner_id
        user_to_save.user_status = get_state(state)
        user_to_save.save(update_fields=["alliance", "in_game_id", "user_status"])
        return user_to_save
    else:
        user = User(user_name=user_name, server=server)
        user.in_game_id = owner_id
        user.alliance = get_alliance(alliance)
        user.save()
        return user


def get_alliance(alliance_tag):
    alliance = Alliance.objects.filter(tag=alliance_tag, server=server)
    if alliance:
        return alliance[0]
    elif alliance_tag:
        alliance = Alliance()
        alliance.tag = alliance_tag
        alliance.save()
        return alliance
    return None


def get_town(town_name, user, island, in_game_id, town_level):
    town = Town.objects.filter(in_game_id=in_game_id, is_deleted=False)
    if town.count() == 1:
        print(f'Town {town_name} ({user}) Island: {island} exists')
        town = town[0]
        town.town_name = town_name
        town.level = town_level
        town.island = island
        town.user = user
        town.save()
        return None
    else:
        town = Town(town_name=town_name, user=user, island=island, in_game_id=in_game_id, level=town_level)
        print("Town %s (%s) created" % (town_name, user))
        return town


def get_state(state):
    if state == 'inactive' or state == 'inactive_banned':
        return UserStatus.objects.get(id=2)
    elif state == 'vacation':
        return UserStatus.objects.get(id=4)
    return UserStatus.objects.get(id=1)


def delete_missing_towns(towns_script, towns_database):
    towns_script_ids = []
    for city in towns_script:
        if city['id'] != -1:
            towns_script_ids.append(city['id'])

    for town in towns_database:
        if (town.in_game_id not in towns_script_ids) and (town.user.user_status and town.user.user_status.id != 3):
            print('Town id=' + str(town.in_game_id) + ' ' + str(town.user.user_name) + ' - DELETED')
            town.is_deleted = True
            town.save()


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
