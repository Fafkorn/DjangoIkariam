from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from ..decorators import admin_only
from ..models import AchievementLevel, AchievementCategory, User, DefaultUsersConnection, UserAchievement


@login_required(login_url='helper:login')
@admin_only()
def get_user_achievements(request, category_id, user_id):
    user = get_object_or_404(User, pk=user_id)
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
    return render(request, 'helper/user_achievements/user_achievements.html', context)


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
    user_id = request.POST['user_id']
    achievement_id = request.POST['id']
    progress = request.POST['progress']
    category = request.POST['category']
    user_achievement = UserAchievement.objects.get(pk=achievement_id)
    user_achievement.progress = progress
    user_achievement.save()
    return HttpResponseRedirect(reverse('helper:achievements_category', args=(user_id, category)))


def get_category_progress(all_achievements, categories_number):
    category_values = [[0, 0] for _ in range(categories_number)]
    for achievement in all_achievements:
        category_values[achievement.achievement_level.achievement.category.id-1][0] += achievement.achievement_level.level
        category_values[achievement.achievement_level.achievement.category.id-1][1] += achievement.achievement_level.achievement.max_level
    return category_values


@login_required(login_url='helper:login')
@admin_only()
def level_up(request):
    user_id = request.POST['user_id']
    user_achievement_id = request.POST['id']
    category_id = request.POST['category']
    user_achievement = UserAchievement.objects.get(pk=user_achievement_id)

    achievement_level = AchievementLevel.objects.get(achievement__id=user_achievement.achievement_level.achievement.id,
                                                     level=user_achievement.achievement_level.level+1)

    user_achievement.achievement_level = achievement_level
    user_achievement.save()
    return HttpResponseRedirect(reverse('helper:achievements_category', args=(user_id, category_id)))
