from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from mysite.helper.models import TownResources


def web_scrap_resources(request):
    text = request.POST['html_data']
    soup = BeautifulSoup(text, 'html.parser')

    town_id = get_town_id(text)
    print(town_id)

    town_resources = TownResources.objects.filter(town__in_game_id=town_id)
    if not town_resources:
        return

    town_resources = town_resources[0]

    wood = get_value_by_html_id(soup, 'js_GlobalMenu_wood_Total')
    wood_production = get_value_by_html_id(soup, 'js_GlobalMenu_resourceProduction')

    wine = get_value_by_html_id(soup, 'js_GlobalMenu_wine_Total')
    tavern_expenses = get_value_by_html_id(soup, 'js_GlobalMenu_WineConsumption')
    wine_production = get_value_by_html_id(soup, 'js_GlobalMenu_production_wine')

    marble = get_value_by_html_id(soup, 'js_GlobalMenu_marble_Total')
    marble_production = get_value_by_html_id(soup, 'js_GlobalMenu_production_marble')

    crystal = get_value_by_html_id(soup, 'js_GlobalMenu_crystal_Total')
    crystal_production = get_value_by_html_id(soup, 'js_GlobalMenu_production_crystal')

    sulfur = get_value_by_html_id(soup, 'js_GlobalMenu_sulfur_Total')
    sulfur_production = get_value_by_html_id(soup, 'js_GlobalMenu_production_sulfur')

    town_resources.wood = wood
    town_resources.wood_production = wood_production
    town_resources.wine = wine
    town_resources.tavern_expenses = tavern_expenses
    town_resources.wine_production = wine_production
    town_resources.marble = marble
    town_resources.marble_production = marble_production
    town_resources.crystal = crystal
    town_resources.crystal_production = crystal_production
    town_resources.sulfur = sulfur
    town_resources.sulfur_production = sulfur_production
    town_resources.save_time = datetime.now()
    town_resources.save()


def get_town_id(html: str) -> Optional[int]:
    search_string = "currentCityId: "
    start = html.find(search_string)
    soup = html[start + len(search_string):]
    last = soup.find(",")
    script_string = soup[0:last]
    try:
        city_id = int(script_string)
    except ValueError:
        return None
    return city_id


def get_user_name(soup: BeautifulSoup) -> Optional[str]:
    for li in soup.find_all('li', {'class': 'avatarName'}):
        for a in li.find_all('a', {'class': 'noViewParameters'}):
            user_name = a.get('title', '')
            if user_name:
                return user_name
    return None


def get_town_name(soup: BeautifulSoup) -> Optional[str]:
    city_name = soup.find('span', {'id': 'js_cityBread'})
    if not city_name:
        return None
    return city_name.text


def get_value_by_html_id(soup: BeautifulSoup, html_id: str) -> Optional[int]:
    html = soup.find('td', {'id': html_id})
    if not html:
        return None
    text = html.text
    text = text.replace(',', '').strip()
    if not text:
        return None
    return int(text)
