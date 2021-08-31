from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from mysite.helper.views.panel import achievements_helper
from ..decorators import admin_only
from ..models import User


@login_required(login_url='helper:login')
@admin_only()
def get_achievements(request):
    users_with_achievements = User.objects.all().annotate(achievements=Sum('userachievement__achievement_level__level')).order_by('-achievements')[:50]
    context = {
        'title': 'Osiągnięcia',
        'users_with_achievements': users_with_achievements
    }
    return render(request, 'helper/achievements.html', context)


@login_required(login_url='helper:login')
def analyze_achievements_data(request):
    achievements_helper.web_scrap_achievements(request)
    return redirect(reverse('helper:achievements'))
