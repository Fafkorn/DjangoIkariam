from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from ..decorators import admin_only
from ..models import AchievementLevel, AchievementCategory, User, DefaultUsersConnection, UserAchievement


@login_required(login_url='helper:login')
@admin_only()
def get_achievements(request, category_id):
    connected_user = DefaultUsersConnection.objects.filter(auth_user=request.user.id)
    user = connected_user[0] if connected_user else User.objects.get(pk=1)
    all_achievements = UserAchievement.objects.filter(user__id=user.id)
    achievements = UserAchievement.objects.filter(user__id=user.id, achievement_level__achievement__category__id=category_id)
    achievements = split_by_completion(achievements)
    achievement_categories = AchievementCategory.objects.all()

    category_progress = get_category_progress(all_achievements, len(achievement_categories))

    context = {'achievements': achievements,
               'achievement_categories': zip(achievement_categories, category_progress),
               'user': user,
               'category': category_id,
               'active_category': int(category_id),
               'nav_active': 'guide',
               'title': 'Osiągnięcia'}
    return render(request, 'helper/achievements/achievements.html', context)


def split_by_completion(achievements):
    done = []
    undone = []
    for achievement in achievements:
        if achievement.achievement_level.level == achievement.achievement_level.achievement.max_level:
            done.append(achievement)
        else:
            undone.append(achievement)
    return undone + done


def confirm_progress(request):
    achievement_id = request.POST['id']
    progress = request.POST['progress']
    category = request.POST['category']
    user_achievement = UserAchievement.objects.get(pk=achievement_id)
    user_achievement.progress = progress
    user_achievement.save()
    return HttpResponseRedirect(reverse('helper:achievements_category', args=(category,)))


def get_category_progress(all_achievements, categories_number):
    category_values = [[0, 0] for _ in range(categories_number)]
    for achievement in all_achievements:
        category_values[achievement.achievement_level.achievement.category.id-1][0] += achievement.achievement_level.level
        category_values[achievement.achievement_level.achievement.category.id-1][1] += achievement.achievement_level.achievement.max_level
    return category_values


@login_required(login_url='helper:login')
@admin_only()
def level_up(request):
    user_achievement_id = request.POST['id']
    category_id = request.POST['category']
    user_achievement = UserAchievement.objects.get(pk=user_achievement_id)

    achievement_level = AchievementLevel.objects.get(achievement__id=user_achievement.achievement_level.achievement.id,
                                                     level=user_achievement.achievement_level.level-1)

    user_achievement.achievement_level = achievement_level
    user_achievement.save()
    return HttpResponseRedirect(reverse('helper:achievements_category', args=(category_id,)))
