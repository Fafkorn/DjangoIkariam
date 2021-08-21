from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from mysite.helper.decorators import admin_only
from mysite.helper.models import User, UserHistory
from django.contrib.auth.decorators import login_required

from mysite.helper.views.panel import island_helper, ranking_helper, town_helper, resources_helper


@login_required(login_url='helper:login')
@admin_only()
def panel_site(request):
    context = {'title': 'Admin'}
    return render(request, 'helper/panel.html', context)


@admin_only()
def analyze_all_islands_data(request):
    island_helper.web_scrap_all_islands(request)
    return HttpResponseRedirect(reverse('helper:admin', args=()))


@admin_only()
def analyze_island_data(request):
    island_helper.web_scrap_island(request)
    return HttpResponseRedirect(reverse('helper:admin', args=()))


@admin_only()
def analyze_ranking_data(request):
    ranking_helper.web_scrap_ranking(request)
    return HttpResponseRedirect(reverse('helper:admin', args=()))


@admin_only()
def analyze_resources_data(request):
    resources_helper.web_scrap_resources(request)
    user_id = request.POST['user_id']
    return HttpResponseRedirect(reverse('helper:user_resources', args=[user_id]))


@login_required(login_url='helper:login')
def analyze_town_data(request):
    user_id = request.POST['user_id']
    town_helper.web_scrap_town(request)
    return redirect(reverse('helper:user_buildings', args=[user_id]))


@login_required(login_url='helper:login')
@admin_only()
def set_all_users_deleted(request):
    User.objects.update(user_status=3)
    return HttpResponseRedirect(reverse('helper:admin', args=()))


@admin_only()
def update_users_ranking_score(request):
    users = User.objects.all()
    users_to_update = []
    for counter, user in enumerate(users):
        history = UserHistory.objects.filter(score__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.score = history[0].score

        history = UserHistory.objects.filter(master_builders__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.master_builders = history[0].master_builders

        history = UserHistory.objects.filter(building_levels__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.building_levels = history[0].building_levels

        history = UserHistory.objects.filter(scientists__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.scientists = history[0].scientists

        history = UserHistory.objects.filter(research_level__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.research_level = history[0].research_level

        history = UserHistory.objects.filter(generals__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.generals = history[0].generals

        history = UserHistory.objects.filter(gold__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.gold = history[0].gold

        history = UserHistory.objects.filter(offensive__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.offensive = history[0].offensive

        history = UserHistory.objects.filter(defensive__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.defensive = history[0].defensive

        history = UserHistory.objects.filter(trading__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.trading = history[0].trading

        history = UserHistory.objects.filter(resources__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.resources = history[0].resources

        history = UserHistory.objects.filter(donations__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.donations = history[0].donations

        history = UserHistory.objects.filter(piracy__gt=-1, user_id=user.id).order_by('-time')
        if history:
            user.piracy = history[0].piracy
        users_to_update.append(user)
    User.objects.bulk_update(users_to_update,
                             ['score', 'master_builders', 'building_levels', 'scientists', 'research_level',
                              'generals', 'gold', 'offensive', 'defensive', 'trading', 'resources', 'donations',
                              'piracy'])

    return HttpResponseRedirect(reverse('helper:admin', args=()))

