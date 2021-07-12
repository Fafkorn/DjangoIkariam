import math

from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.shortcuts import render, get_object_or_404
from .filters import IslandFilter

from ..models import Island, User, Town


def get_islands(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    x = request.GET.get('x', '')
    y = request.GET.get('y', '')
    luxury_resource = request.GET.get('luxury_resource', '')
    wood_level = request.GET.get('wood_level', '')
    luxury_level = request.GET.get('luxury_level', '')
    order_by = request.GET.get('order_by', '')
    has_tower = request.GET.get('has_tower', '')
    islands_list = Island.objects.filter().order_by('wood_level', 'luxury_level').reverse().annotate(towns=Count('town'))
    my_filter = IslandFilter(request.GET, queryset=islands_list)
    islands_list = my_filter.qs
    towns = islands_list.aggregate(sum=Sum('towns'))['sum']
    islands_found = islands_list.count

    results_on_page = 15
    paginator = Paginator(islands_list, results_on_page)
    page_num = int(request.GET.get('page', 1))
    page = paginator.page(page_num)

    has_pages = math.ceil(islands_list.count() / results_on_page)

    buttons = get_buttons(page_num, has_pages)

    context = {'islands_list': page,
               'my_filter': my_filter,
               'user': user, 'user_id': user_id,
               'x': x,
               'y': y,
               'towns': towns,
               'luxury_resource': luxury_resource,
               'wood_level': wood_level,
               'luxury_level': luxury_level,
               'order_by': order_by,
               'has_tower': has_tower,
               'islands_found': islands_found,
               'page_num': int(page_num),
               'has_pages': has_pages,
               'buttons': buttons,
               'nav_active':  'islands'}

    return render(request, 'helper/islands.html', context)


def get_buttons(page, has_pages):
    buttons = []
    if has_pages < 12:
        for i in range(has_pages):
            buttons.append(i + 1)
        return buttons
    elif page <= 6:
        for i in range(9):
            buttons.append(i + 2)
        buttons.append(0)
    elif (page > 6) and (page <= has_pages-7):
        buttons.append(0)
        for i in range(9):
            buttons.append(page-4+i)
        buttons.append(0)
    elif page > has_pages-7:
        buttons.append(0)
        for i in range(9):
            buttons.append(has_pages-9+i)
    buttons.insert(0, 1)
    buttons.append(has_pages)
    return buttons
