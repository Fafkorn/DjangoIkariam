from bs4 import BeautifulSoup

from mysite.helper.models import UserStatus, UserHistory, User
from datetime import datetime

titles = ['Pan Cieni', 'Imperator', 'Mistrz Sztuk Pięknych', 'Geniusz', 'Korsarz', 'Ambasador', 'Mecenas',
              'Bicz Barbarzyńców', 'Najwyższy Namiestnik', 'Strażnik Wiedzy', 'Hurtownik', 'Syzyf', 'Burmistrz',
              'Maratończyk', 'Łatacz Żagli', 'Cudowne Dziecko', 'Pan Kopalni Kryształu', 'Szczur Laboratoryjny',
              'Gubernator', 'Kolekcjoner punktów', 'Postrach Oceanów', 'Ulubieniec Apollona', 'Admirał',
              'Supermózg', 'Miłośnik Sztuki', 'Szpieg', 'Pan Winorośli', 'Skarbnik Króla Midasa',
              'Pan Kopalni Siarki', 'Pan Tartaków', 'Reformator', 'Kapitan Piratów', 'Pogromca Herkulesa',
              'Duma Hermesa', 'Szef Kuchni', 'Król Handlarzy Bronią', '007']

ranking_types = ['Całkowity wynik', 'Mistrzowie budowy', 'Poziomy budynków', 'Naukowcy', 'Poziomy badań',
                 'Generałowie', 'Zapas złota', 'Punkty ofensywy', 'Punkty obrony', 'Handlarz', 'Surowce',
                 'Datki', 'Punkty Abordażu']


def web_scrap_ranking(request):
    text = request.POST['html_data']
    soup = BeautifulSoup(text, 'html.parser')

    ranking_type = get_ranking_type(soup)

    names, statuses = get_names_and_statuses(soup)
    alliances = get_alliances(soup)
    scores = get_scores(soup)

    data = zip(names, alliances, scores, statuses)
    save_data(data, ranking_type)


def set_users_history_appropriate_ranking_value(user_history, ranking_type, value):
    if 'Całkowity wynik' in ranking_type:
        user_history.score = value
    elif 'Mistrzowie budowy' in ranking_type:
        user_history.master_builders = value
    elif 'Poziomy budynków' in ranking_type:
        user_history.building_levels = value
    elif 'Naukowcy' in ranking_type:
        user_history.scientists = value
    elif 'Poziomy badań' in ranking_type:
        user_history.research_level = value
    elif 'Generałowie' in ranking_type:
        user_history.generals = value
    elif 'Zapas złota' in ranking_type:
        user_history.gold = value
    elif 'Punkty ofensywy' in ranking_type:
        user_history.offensive = value
    elif 'Punkty obrony' in ranking_type:
        user_history.defensive = value
    elif 'Handlarz' in ranking_type:
        user_history.trading = value
    elif 'Surowce' in ranking_type:
        user_history.resources = value
    elif 'Datki' in ranking_type:
        user_history.donations = value
    elif 'Punkty Abordażu' in ranking_type:
        user_history.piracy = value


def get_status(element):
    if element.find('a').get('class') and 'gray' in element.find('a').get('class'):
        return 2
    elif element.find('img'):
        return 4
    else:
        return 1


def get_ranking_type(soup: BeautifulSoup) -> str:
    option_list = soup.find_all("span", {"class": "dropDownButton"})
    for option in option_list:
        for ranking_type in ranking_types:
            if ranking_type in option.text:
                return option.text


def get_names_and_statuses(soup: BeautifulSoup):
    names = []
    statuses = []
    td_name = soup.find_all("td", {"class": "name"})
    for element in td_name:
        name = element.text
        statuses.append(get_status(element))
        for title in titles:
            name = name.replace(title, '')
        names.append(name.strip())
        print(f"{name.strip()} {get_status(element)}")
    return names, statuses


def get_alliances(soup: BeautifulSoup):
    alliances = []
    td_ally = soup.find_all("td", {"class": "allytag"})
    for element in td_ally:
        alliance = element.text.replace('\n', '')
        alliance = alliance.strip()
        alliances.append(alliance)
    return alliances


def get_scores(soup: BeautifulSoup):
    scores = []
    td_score = soup.find_all("td", {"class": "score"})
    for element in td_score:
        scores.append(element.text.replace(',', ''))
    return scores


def save_data(data, ranking_type):
    user_statuses = UserStatus.objects.all()
    user_histories_to_create = []
    user_histories_to_update = []
    users_to_update = []
    for entry in data:
        create_flag = False
        user = User.objects.filter(user_name=entry[0])
        if user:
            user = user[0]
            user.alliance = entry[1]
        else:
            user = User(user_name=entry[0], alliance=entry[1])
            user.alliance = entry[1]
            user.save()
            user = User.objects.filter(user_name=entry[0])
            user = user[0]

        today = datetime.now()
        user_history = UserHistory.objects.filter(user__id=user.id, time__year=today.year, time__month=today.month,
                                                  time__day=today.day)
        if user_history:
            user_history = user_history[0]
        else:
            user_history = UserHistory()
            create_flag = True
        user_history.time = datetime.now()
        user_history.user = user
        set_users_history_appropriate_ranking_value(user_history, ranking_type, entry[2])
        user.user_status = get_user_status_object(user_statuses, entry[3])
        users_to_update.append(user)
        if create_flag:
            user_histories_to_create.append(user_history)
        else:
            user_histories_to_update.append(user_history)

    User.objects.bulk_update(users_to_update, ['alliance', 'user_status'])
    UserHistory.objects.bulk_create(user_histories_to_create)
    UserHistory.objects.bulk_update(user_histories_to_update, ['time', 'score', 'master_builders', 'building_levels',
                                                               'scientists', 'research_level', 'generals', 'gold',
                                                               'offensive', 'defensive', 'trading', 'resources',
                                                               'donations', 'piracy'])


def get_user_status_object(user_statuses, user_status_id):
    for user_status in user_statuses:
        if user_status.id == user_status_id:
            return user_status
    return None

