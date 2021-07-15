from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import math
from .filters import UserFilter
from django.contrib.auth.decorators import login_required

from ..models import User


@login_required(login_url='helper:login')
def get_users(request):
    visited_users = User.objects.order_by('last_visit').reverse()[:10]
    my_filter = UserFilter(request.GET, queryset=User.objects.order_by('score').reverse())

    user_name = request.GET.get('user_name', '')
    alliance = request.GET.get('alliance', '')
    user_status = request.GET.get('user_status', '')
    order_by = request.GET.get('order_by', '')

    users_list = my_filter.qs
    results_on_page = 100
    paginator = Paginator(users_list, results_on_page)
    page_num = request.GET.get('page', 1)
    page = paginator.page(page_num)

    user = User.objects.get(pk=1)

    has_pages = math.ceil(users_list.count() / results_on_page)
    buttons = []
    for i, val in enumerate(range(has_pages)):
        buttons.append([int((i+1)*results_on_page), int(i+1)])
    context = {'users_list': page,
               'user': user,
               'my_filter': my_filter,
               'user_name': user_name,
               'alliance': alliance,
               'user_status': user_status,
               'order_by': order_by,
               'visited_users': visited_users,
               'buttons': buttons, 'page_num': int(page_num),
               'nav_active': 'users',
               'title': 'Użytkownicy'
               }
    return render(request, 'helper/users.html', context)


def add_user(request):
    user_name = request.POST['user_name']
    user = User(user_name=user_name)
    user.save()
    return HttpResponseRedirect(reverse('helper:users', args=()))
