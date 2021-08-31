from bs4 import BeautifulSoup

from mysite.helper.models import AchievementCategory, UserAchievement, User, AchievementLevel

ids = [[2, 4, 6, 7, 8, 9, 23, 24, 35, 40, 43],
       [5, 11, 19, 20, 33, 34],
       [12, 13, 14, 15, 16, 17, 18, 36],
       [100, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132],
       [1, 3, 21, 26, 27, 28, 29, 32, 38, 39, 41, 44, 45, 46, 701, 702, 703, 704, 705, 706, 707, 708, 810, 811, 813, 814, 815, 816],
       [42, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 315, 319, 501, 502, 503, 504, 505, 506, 507, 508, 509, 512, 513, 515],
       [201, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619]]


def web_scrap_achievements(request):
    text = request.POST['html_data']
    soup = BeautifulSoup(text, 'html.parser')
    user = get_user(soup)
    category = get_category(soup)
    achievements = get_achievements(soup, category)
    user_achievements = []
    for achievement in achievements:
        ua = UserAchievement()
        ua.achievement_level = achievement
        ua.user = user
        user_achievements.append(ua)
    UserAchievement.objects.filter(user__id=user.id, achievement_level__achievement__category__id=category.id).delete()
    UserAchievement.objects.bulk_create(user_achievements)


def get_user(soup: BeautifulSoup):
    h3 = soup.find("h3", {"id": "categoryCompareTitle"})
    spans = h3.find_all("span")
    for span in spans:
        if 'Porównaj z ' in span.text:
            span_text = span.text
            user_name = span_text.replace('Porównaj z ', '')
            user = User.objects.filter(user_name=user_name)[0]
            return user
    return None


def get_achievements(soup: BeautifulSoup, category: AchievementCategory):
    achievements = []
    soup = soup.find("table", {"id": "achievementsTable"})
    for i in ids[category.id - 1]:
        achievement = get_achievement(soup, i, category)
        if achievement:
            achievements.append(achievement)
    return achievements


def get_achievement(soup: BeautifulSoup, achievement_id: int, category: AchievementCategory):
    name_div = soup.find("div", {"id": "achievement_" + str(achievement_id) + "_name"})
    if not name_div:
        return None
    span = name_div.find("span")
    name = span.text
    level = soup.find("div", {"id": "achievement_" + str(achievement_id) + "_nextLevel"})
    if level:
        level_text = level.text.replace('Poziom ', '')
    else:
        level_text = 0
    return AchievementLevel.objects.filter(achievement__name=name, level=level_text, achievement__category__id=category.id)[0]


def get_category(soup: BeautifulSoup):
    h3 = soup.find("h3", {"id": "categoryCompareTitle"})
    span = h3.find("span")
    span.extract()
    h3_text = h3.text
    h3_text = h3_text.replace('Kategorie ', '').replace(':', '').strip()
    achievement_category = AchievementCategory.objects.filter(name=h3_text)[0]
    return achievement_category
