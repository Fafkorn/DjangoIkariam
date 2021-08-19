from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from mysite.helper.decorators import admin_only
from mysite.helper.models import User
from django.contrib.auth.decorators import login_required

from mysite.helper.views.panel import island_helper, ranking_helper, town_helper


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
