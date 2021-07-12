from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ...models import AchievementLevel, AchievementCategory, User, Achievement


def get_achievements(request, category_id):
    user = User.objects.get(id=1)
    # category = request.GET.get('category', 1)
    achievements = AchievementLevel.objects.raw('SELECT * FROM helper_achievementlevel as al INNER JOIN helper_achievement as a on a.id == al.achievement_id WHERE ((al.level == a.level and a.level == a.max_level) OR al.level == a.level+1) AND a.category_id == %s', [category_id])
    achievement_categories = AchievementCategory.objects.all()

    # init()

    cursor = connection.cursor()
    cursor.execute(
        "SELECT SUM(a.level), SUM(a.max_level) FROM helper_achievement AS a GROUP BY a.category_id")
    category_progress = cursor.fetchall()

    achievements_to_do, achievements_done = split_achievements(achievements)
    context = {'achievements_to_do': achievements_to_do,
               'achievements_done': achievements_done,
               'achievement_categories': zip(achievement_categories, category_progress),
               'user': user,
               'category': category_id,
               'active_category': int(category_id),
               'nav_active': 'guide'}
    return render(request, 'helper/guide/achievements.html', context)


def init():
    ach = Achievement.objects.filter(name='Niszczyciel: Balonowiec')
    ach = ach[0]
    levels = ['Zniszcz: 25 jednostek typu Balonowiec.',
              'Zniszcz: 400 jednostek typu Balonowiec.',
              'Zniszcz: 1,000 jednostek typu Balonowiec.',
              'Zniszcz: 2,500 jednostek typu Balonowiec.',
              'Zniszcz: 10,000 jednostek typu Balonowiec.',
              'Zniszcz: 100,000 jednostek typu Balonowiec.'
              ]
    i = 1
    for level in levels:
        achLevel = AchievementLevel()
        achLevel.level = i
        achLevel.achievement = ach
        achLevel.description = level
        # achLevel.save()
        i += 1


def confirm_progress(request):
    achievement_id = request.POST['id']
    progress = request.POST['progress']
    category = request.POST['category']
    achievement = Achievement.objects.get(pk=achievement_id)
    achievement.progress = progress
    achievement.save()
    return HttpResponseRedirect(reverse('helper:achievements_category', args=(category,)))


def split_achievements(achievements):
    achievements_to_do = []
    achievements_done = []
    for achievement in achievements:
        if achievement.achievement.level == achievement.achievement.max_level:
            achievements_done.append(achievement)
        else:
            achievements_to_do.append(achievement)
    return achievements_to_do, achievements_done


def level_up(request):
    achievement_id = request.POST['id']
    category = request.POST['category_id']
    achievement = Achievement.objects.get(pk=achievement_id)
    achievement.level += 1
    achievement.save()
    return HttpResponseRedirect(reverse('helper:achievements_category', args=(category,)))
