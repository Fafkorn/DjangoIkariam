from django.db import connection
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q

from ..models import User, Town

from django.shortcuts import get_object_or_404, render


@login_required(login_url='helper:login')
def get_resources_rank(request, user_id):
    order = request.GET.get('order', 'all')
    user = get_object_or_404(User, pk=user_id)
    resources_by_user = get_resources_by_user(order)[:100]
    context = {
        'user': user,
        'user_id': user_id,
        'resources_by_user': resources_by_user,
        'order': order,
        'title': 'Ranking surowców'
    }
    return render(request, 'helper/resources_rank.html', context)


def get_resources_by_user(order):
    return Town.objects.all().annotate(user_name=F('user__user_name'), userid=F('user__id')).values('user_name', 'userid').annotate(wood=Sum('island__wood_level__workers')).annotate(luxury=Sum('island__luxury_level__workers')).annotate(all=F('wood') + F('luxury')).annotate(wine=Sum('island__luxury_level__workers', filter=Q(island__luxury_resource__id=2))).annotate(marble=Sum('island__luxury_level__workers', filter=Q(island__luxury_resource__id=3))).annotate(crystal=Sum('island__luxury_level__workers', filter=Q(island__luxury_resource__id=4))).annotate(sulfur=Sum('island__luxury_level__workers', filter=Q(island__luxury_resource__id=5))).order_by(f'-{order}')

