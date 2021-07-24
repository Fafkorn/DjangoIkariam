import requests
import time
from django.shortcuts import render, redirect
import json
from django.http import HttpResponseRedirect
from django.urls import reverse

from ..decorators import admin_only
from ..models import User, Town, Resource, Miracle, Island, Building, BuildingInstance, UserStatus
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required


@login_required(login_url='helper:login')
@admin_only()
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


@admin_only()
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


@admin_only()
def web_scrap_island(request):
    text = request.POST['textarea']
    if text == 'kopiuj':
        copy_data_base()
    else:
        soup = BeautifulSoup(text, 'html.parser')
        scripts = soup.find_all("script", {"type": "text/javascript"})
        convert_island_script_to_data(scripts)
    return HttpResponseRedirect(reverse('helper:admin', args=()))


def copy_data_base():
    #create_users()
    # user_statuses = UserStatus.objects.all()
    # user_statuses_to_save = []
    # print('user_statuses_to_save = []')
    # for user_status in user_statuses:
    #     print(f'user_statuses_to_save.append(UserStatus(id={user_status.id}, user_status_name="{user_status.user_status_name}"))')
    # print('UserStatus.obejects.bulk_create(user_statuses_to_save)')


    users = User.objects.all()
    counter = 0
    print('users_to_save = []')
    for user in users:
        if counter == 500:
            break
        print(f'users_to_save.append(User(id={user.id}, user_name="{user.user_name}", user_status=UserStatus.objects.get(pk={user.user_status.id}), shipping_future="{user.shipping_future}"))')
        counter += 1
    print('User.objects.bulk_create(users_to_save)')


def create_user_statuses():
    user_statuses_to_save = []
    user_statuses_to_save.append(UserStatus(id=1, user_status_name="Aktywny"))
    user_statuses_to_save.append(UserStatus(id=2, user_status_name="Nieaktywny"))
    user_statuses_to_save.append(UserStatus(id=3, user_status_name="Usunięty"))
    user_statuses_to_save.append(UserStatus(id=4, user_status_name="Urlop"))
    UserStatus.obejects.bulk_create(user_statuses_to_save)


def create_users():
    users_to_save = []
    users_to_save.append(
        User(id=1, user_name="Fafkorn", user_status=UserStatus.objects.get(pk=1), shipping_future="25"))
    users_to_save.append(
        User(id=2, user_name="davidini", user_status=UserStatus.objects.get(pk=1), shipping_future="25"))
    users_to_save.append(User(id=4, user_name="PiotrW", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=5, user_name="FROSTBITE2", user_status=UserStatus.objects.get(pk=1), shipping_future="4"))
    users_to_save.append(User(id=6, user_name="Graves", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=7, user_name="Kristo", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=8, user_name="Biel2u", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=9, user_name="Pitheros", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=10, user_name="andrut", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=11, user_name="Conan", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=12, user_name="marioosz", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=13, user_name="misiaczek", user_status=UserStatus.objects.get(pk=1), shipping_future="25"))
    users_to_save.append(
        User(id=14, user_name="Energetyk", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=15, user_name="Heisenberg", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=16, user_name="marcel", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=17, user_name="malpiak", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=18, user_name="marlenka", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=19, user_name="Borysek I", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=20, user_name="Fine Shiri", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=22, user_name="orr", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=23, user_name="Ent", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=24, user_name="Numitor", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=25, user_name="nano", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=26, user_name="Qaz", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=27, user_name="thebestkris", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=28, user_name="Cin", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=29, user_name="Kalika", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=30, user_name="Hubert 33", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=31, user_name="Dziadek11", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=32, user_name="nasuada", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=33, user_name="MrocznyKosiarz", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=34, user_name="nettI", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=36, user_name="pzibi056", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=37, user_name="Matiasz", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=38, user_name="yogin", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=39, user_name="SHAKUR", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=40, user_name="turbolit", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=41, user_name="lenon", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=42, user_name="RobiK93", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=43, user_name="kangurek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=44, user_name="MalaCzarna", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=45, user_name="don vito", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=46, user_name="kaliś", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=47, user_name="Afrodyta", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=48, user_name="Mondi", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=49, user_name="Titanus1", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=50, user_name="darkus757", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=51, user_name="mino", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=52, user_name="Baca", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=53, user_name="Bagiecia", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=54, user_name="BOB", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=55, user_name="miki78", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=56, user_name="TITO", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=57, user_name="tetryk", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=58, user_name="WoT", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=59, user_name="WISUS", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=60, user_name="OTTOJA", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=61, user_name="lumen123", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=62, user_name="qsy", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=63, user_name="Zoltar", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=64, user_name="Sagittarius", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=65, user_name="krisu", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=66, user_name="TECHNOLAND", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=67, user_name="Baśka", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=68, user_name="maruss", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=69, user_name="krzysiek06", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=70, user_name="Izaa", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=71, user_name="Gemini", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=72, user_name="CYCERO", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=73, user_name="Bartoo", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=74, user_name="Vini", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=75, user_name="ruter", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=76, user_name="Fabiszon", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=77, user_name="Książe Dudo", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=78, user_name="VETERAN", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=80, user_name="Kesiek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=81, user_name="grzigrzi", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=82, user_name="lordi", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=83, user_name="maniekmaniek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=84, user_name="Baku001", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=85, user_name="beno", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=86, user_name="Martin Astro", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=87, user_name="Zeus52", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=88, user_name="TWARDZIEL", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=89, user_name="dbo", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=90, user_name="Jowisz34", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=92, user_name="Snufkin", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=93, user_name="Carlla", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=94, user_name="bahzm", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=95, user_name="rafi2002", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=96, user_name="isny", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=97, user_name="limarkus", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=98, user_name="Zielocobra", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=99, user_name="bartek33", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=100, user_name="00szymon", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=101, user_name="Raptor", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=102, user_name="Aegir", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=103, user_name="zibi57", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=104, user_name="Qwer", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=105, user_name="Tom", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=106, user_name="Kaper", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=107, user_name="Rang", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=108, user_name="OSTATNI", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=109, user_name="marek2286", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=110, user_name="Nasir", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=111, user_name="wojtaszek13", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=112, user_name="airp", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=113, user_name="Duch i Mrok", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=114, user_name="Awatar Mroku", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=115, user_name="Jarodek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=116, user_name="rafalwoj", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=117, user_name="hermiona006", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=118, user_name="andyt", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=119, user_name="GOREK", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=120, user_name="Putas", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=121, user_name="Valus", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=122, user_name="Stalker", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=123, user_name="Pretender", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=124, user_name="Arkad", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=125, user_name="President", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=126, user_name="MaX", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=127, user_name="koto", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=128, user_name="grom14", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=129, user_name="pawel8", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=130, user_name="Donaldson", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=131, user_name="LEONIDAS I", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=132, user_name="giovanna", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=133, user_name="mgr esmilski", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=134, user_name="sewen", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=135, user_name="Dark Gabriel", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=136, user_name="Norah", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=137, user_name="Tomek sikora", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=138, user_name="BoogeyMan", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=139, user_name="Sinaloa", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=140, user_name="bartoszz", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=141, user_name="Włoch", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=142, user_name="mic5hal", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=143, user_name="RABA", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=144, user_name="Busken", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=145, user_name="MCHIL", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=146, user_name="Nikt", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=147, user_name="abcd", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=148, user_name="anana", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=149, user_name="Elafilos", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=150, user_name="Sulejman Szary", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=151, user_name="Mauser", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=152, user_name="chosen one", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=153, user_name="cyngiel", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=154, user_name="Scarface", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=155, user_name="delwelek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=157, user_name="sulek", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=158, user_name="achim", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=159, user_name="Robert_Ranger", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=160, user_name="Gand", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=162, user_name="jackwar", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=163, user_name="Hitek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=164, user_name="Neomolka", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=165, user_name="andriu1985i", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=166, user_name="Smily", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=167, user_name="Agent Smith", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=168, user_name="bobas", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=169, user_name="Czarny Pan", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=170, user_name="Magoor", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=171, user_name="Crag", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=172, user_name="tomkuba", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=173, user_name="rybol", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=174, user_name="Arecki", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=175, user_name="spartakus_", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=176, user_name="MAR25", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=177, user_name="Danies", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=178, user_name="plebann", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=179, user_name="STONE I", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=180, user_name="peter", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=181, user_name="kamis", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=182, user_name="lool", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=183, user_name="Makavelli", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=184, user_name="JOGI", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=186, user_name="marko", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=187, user_name="-Czarodziej-", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=188, user_name="mazda21", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=189, user_name="Legolas1993", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=190, user_name="Simonides", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=191, user_name="arkadius_00", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=192, user_name="ireneos", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=193, user_name="dracke", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=194, user_name="trebor38", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=195, user_name="Agesilaos", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=196, user_name="Dunpeal", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=197, user_name="icemanwlkp", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=198, user_name="chris296", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=199, user_name="Narrator", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=200, user_name="fusion", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=201, user_name="slowik1891", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=202, user_name="Yamashita74", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=203, user_name="elixir", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=204, user_name="kg1983", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=205, user_name="piotr11234", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=206, user_name="pijawka", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=207, user_name="spectrum", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=208, user_name="pysiaaa", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=209, user_name="Maryka111", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=210, user_name="marek102", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=211, user_name="jakobsjw1400", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=212, user_name="Marcin7312", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=213, user_name="HEKTORYN", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=214, user_name="dziki011", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=215, user_name="mamaj12", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=216, user_name="Kameleon", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=217, user_name="nikadela1", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=218, user_name="dandi", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=219, user_name="miku69", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=220, user_name="Gracz", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=221, user_name="mikethegreat", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=222, user_name="Wilda", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=223, user_name="Kuba_1997", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=224, user_name="galonska", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=225, user_name="Wzorowy", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=226, user_name="Wallander", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=227, user_name="kuki23", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=228, user_name="Mr Hyde", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=230, user_name="Bakusek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=231, user_name="rudy1234", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=232, user_name="stefanos1", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=233, user_name="marianbelchatow", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=234, user_name="Tyrion", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=235, user_name="pojawiamsie", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=236, user_name="mysz", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=237, user_name="Buntownik", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=238, user_name="sire", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=239, user_name="wea", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=240, user_name="Jan1212", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=241, user_name="w124", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=242, user_name="ppawela", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=243, user_name="Prince", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=244, user_name="k1ller", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=245, user_name="zwierzoo", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=246, user_name="MikaTika", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=247, user_name="Alex wielki", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=248, user_name="kriszag", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=249, user_name="wulkan098", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=250, user_name="Falangista", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=251, user_name="Irma", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=252, user_name="Ponowa", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=253, user_name="Barto875", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=254, user_name="focus10", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=255, user_name="Spyro", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=256, user_name="Jacor-s", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=257, user_name="mrmasel", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=258, user_name="XSzkottX", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=259, user_name="Anakin", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=260, user_name="Krzysiek2019", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=261, user_name="W S", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=262, user_name="Roman 37", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=263, user_name="suds", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=264, user_name="Spartan III", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=265, user_name="Rusek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=266, user_name="Angels", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=267, user_name="Monka", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=268, user_name="qku z-13-", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=269, user_name="byczek_24", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=270, user_name="Pomagier", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=271, user_name="mcalay", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=272, user_name="alex-z", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=273, user_name="Roman10", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=274, user_name="Jarovonskala", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=275, user_name="ela120364", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=276, user_name="Wypcio", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=277, user_name="Maltese", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=278, user_name="siwy111", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=279, user_name="Mormon", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=280, user_name="novice", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=281, user_name="Franklin", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=282, user_name="Wulfgar", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=283, user_name="vodafonik", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=284, user_name="Hubert", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=285, user_name="alania102", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=286, user_name="lukpol18", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=287, user_name="jano", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=288, user_name="QUICK ONE", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=289, user_name="ASTERIXX", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=290, user_name="gripex", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=291, user_name="wacek123453", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=292, user_name="Kirke", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=293, user_name="voooc", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=294, user_name="Lord Voldemort", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=295, user_name="bastion100", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=296, user_name="Rudy Wiewiór", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=297, user_name="Stiv", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=298, user_name="Ogolona", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=299, user_name="stawar", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=300, user_name="maris", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=301, user_name="luk254", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=302, user_name="andrew", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=303, user_name="rataj", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=304, user_name="apacz", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=305, user_name="Hercules-Kal-EL", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=306, user_name="-p-", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=307, user_name="Rosiczka", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=308, user_name="Iena", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=309, user_name="stoy", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=310, user_name="Ajax", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=311, user_name="jondm", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=312, user_name="kurczak", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=313, user_name="Tompa", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=314, user_name="mati442", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=315, user_name="lisc", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=316, user_name="irek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=317, user_name="kary27", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=319, user_name="kwasu", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=320, user_name="andrzej2007", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=321, user_name="Samozłooo", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=322, user_name="killer222", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=323, user_name="trojan", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=324, user_name="theandrewip", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=325, user_name="marcin1983", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=326, user_name="Grisza1981", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=327, user_name="Bilbao", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=328, user_name="NightEvil", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=329, user_name="pgrabek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=330, user_name="Lukys", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=331, user_name="teardrop", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=332, user_name="Roland69", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=333, user_name="MORIANY", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=334, user_name="włóczykij66", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=335, user_name="valkiria", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=336, user_name="QUANTUM678", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=337, user_name="Ariss", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=339, user_name="Diabloo", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=340, user_name="smetanapub", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=341, user_name="Radoslaf", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=342, user_name="wang", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=343, user_name="Danny", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=344, user_name="Rossi", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=345, user_name="_ksiadz_", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=346, user_name="bania", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=347, user_name="Venus", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=348, user_name="peter666", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=349, user_name="kicaj19", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=350, user_name="aneri", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=351, user_name="Katrinka", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=352, user_name="mati95", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=353, user_name="masterr", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=354, user_name="Zołza", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=355, user_name="alex1", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=356, user_name="Piotruś80", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=357, user_name="dono", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=358, user_name="lenek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=359, user_name="ingaaa", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=360, user_name="Wiking II", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=361, user_name="grzmotek1234559", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=362, user_name="Suzuki", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=363, user_name="kambur", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=364, user_name="Rommmek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=365, user_name="Maber", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=366, user_name="placko", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=367, user_name="McSpawn", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=368, user_name="torbal", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=369, user_name="jony03", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=370, user_name="Pymek", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=371, user_name="hucz", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=372, user_name="zielonyyy838", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=373, user_name="Destroyer", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=374, user_name="tom138", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=375, user_name="Atena33", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=376, user_name="Albus Dumbledor", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=377, user_name="ben", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=378, user_name="Frogs", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=379, user_name="pretorian-Ś-", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=380, user_name="cinek_", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=381, user_name="Siuks", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=382, user_name="Romek", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=383, user_name="Binio", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=384, user_name="AAA", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=385, user_name="Spartacus", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=386, user_name="Kynio", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=387, user_name="LEM", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=388, user_name="Masterka", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=389, user_name="colombo", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=390, user_name="Gold", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=391, user_name="Genior", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=392, user_name="Demon Mroku", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=393, user_name="Piwożłop", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=394, user_name="Musashi", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=395, user_name="Pijany Mistrz", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=396, user_name="Tamburyn", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=397, user_name="kazio", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=398, user_name="CHROM", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=399, user_name="123szymon", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=400, user_name="zulus", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=401, user_name="VanDeJac", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=402, user_name="Jony", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=403, user_name="Esuman", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=404, user_name="Tatiana", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=405, user_name="Thorgall", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=406, user_name="krzych13", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=407, user_name="Casian", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=408, user_name="Xenia", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=409, user_name="ToJaZielak", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=410, user_name="zacharus", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=411, user_name="niusia_1982", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=412, user_name="Malena", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=413, user_name="Dawid_Kolarz", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=414, user_name="Joszua", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=415, user_name="Tzar", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=416, user_name="K r u k", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=417, user_name="Demon Nocy", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=418, user_name="Freya", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=419, user_name="CzarnaMoc", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=421, user_name="Ambasta", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=422, user_name="Ola28", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=423, user_name="sirbl", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=424, user_name="Fabiana", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=425, user_name="sekretgrace", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=426, user_name="lichwiasz150", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=427, user_name="Worker", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=428, user_name="Iberia", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=429, user_name="melnar76", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=430, user_name="GIGANT", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=431, user_name="JERRY", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=432, user_name="pedziwiatr", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=433, user_name="CIACHO", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=435, user_name="Puszkolo", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=436, user_name="kleo", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=437, user_name="Ulekqqq", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=438, user_name="Bazyli", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=439, user_name="Dareczek25l", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=440, user_name="natka3454", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=441, user_name="spartiata", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=442, user_name="LisbethSalander", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=443, user_name="Kajfasz", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=444, user_name="Demo", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=445, user_name="Grzechu", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=447, user_name="Infiniti", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=448, user_name="flo", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=449, user_name="Dethpool", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=450, user_name="GI Erni97", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=451, user_name="Fargo", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=452, user_name="patii", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=453, user_name="Benek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=454, user_name="ober", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=455, user_name="Doe", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=456, user_name="Kahlan", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=457, user_name="Beata", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=458, user_name="Nerwus", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=459, user_name="cichy", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=460, user_name="root", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=461, user_name="szaq79", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=462, user_name="Kotty", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=463, user_name="RememberMe86", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=464, user_name="kukal", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=465, user_name="szpaczek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=466, user_name="franky97", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=467, user_name="Lagarto", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(
        User(id=468, user_name="kuba071095", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=469, user_name="Akitsuki", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=470, user_name="Rexus", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=471, user_name="MESPEED", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=472, user_name="hooli", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=473, user_name="Pitter", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=474, user_name="sewerix", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=475, user_name="Berzerk", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=476, user_name="k0br3tti", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=477, user_name="Amenhotep", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=478, user_name="Asuna", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=479, user_name="JARZOL", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=480, user_name="Keen", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=481, user_name="Ernest", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=482, user_name="miodzio",
                              user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=483, user_name="paniwladca", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=484, user_name="xchild", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(User(id=485, user_name="hacha", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=486, user_name="Hogtied", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(User(id=487, user_name="magic", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=488, user_name="celtic", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(User(id=489, user_name="hance", user_status=UserStatus.objects.get(pk=2), shipping_future="0"))
    users_to_save.append(User(id=490, user_name="tina", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=491, user_name="kowalusek", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=492, user_name="Małgorzata", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=493, user_name="Grzesiek2", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=494, user_name="Mały Zabijaka", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=495, user_name="Wolverine", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=496, user_name="maxxxxx", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=497, user_name="nina0226", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=499, user_name="Kordelius", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=500, user_name="Arvena", user_status=UserStatus.objects.get(pk=4), shipping_future="0"))
    users_to_save.append(
        User(id=501, user_name="Ragazza", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=502, user_name="Pyciek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=503, user_name="ZiembuS", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=504, user_name="Harcyda", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=505, user_name="Atlas-8476", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=506, user_name="pic2ek", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=507, user_name="szynkers", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=508, user_name="exsaracen", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=509, user_name="kalima", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=510, user_name="tadewausz", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=511, user_name="Dragunow", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=512, user_name="Barzena", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=513, user_name="szakal_dd", user_status=UserStatus.objects.get(pk=3), shipping_future="0"))
    users_to_save.append(
        User(id=514, user_name="vinnetou2", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))
    users_to_save.append(
        User(id=515, user_name="Ares-WS", user_status=UserStatus.objects.get(pk=1), shipping_future="0"))

    User.objects.bulk_create(users_to_save)


@admin_only()
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


@admin_only()
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


@login_required(login_url='helper:login')
def web_scrap_town(request):
    text = request.POST['html']
    user_id = request.POST['user_id']
    soup = BeautifulSoup(text, 'html.parser')
    scripts = soup.find_all("script", {"type": "text/javascript"})
    convert_town_script_to_data(scripts)
    return redirect(reverse('helper:user_buildings', args=[user_id]))


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


@login_required(login_url='helper:login')
@admin_only()
def set_all_users_deleted(request):
    User.objects.update(user_status=3)
    return HttpResponseRedirect(reverse('helper:admin', args=()))
