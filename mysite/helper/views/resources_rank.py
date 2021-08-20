from django.db import connection
from django.contrib.auth.decorators import login_required

from ..models import User

from django.shortcuts import get_object_or_404, render


@login_required(login_url='helper:login')
def get_resources_rank(request, user_id):
    order = request.GET.get('order', 'all_workers')
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
    cursor = connection.cursor()
    cursor.execute(
        "SELECT u.id, u.user_name, SUM(s.workers)+SUM(m.workers) AS all_workers, SUM(s.workers) AS wood_workers, SUM(m.workers) AS luxury_workers, SUM(CASE WHEN i.luxury_resource_id = 2 THEN m.workers ELSE 0 END) as wine_workers, SUM(CASE WHEN i.luxury_resource_id = 3 THEN m.workers ELSE 0 END) as marble_workers, SUM(CASE WHEN i.luxury_resource_id = 4 THEN m.workers ELSE 0 END) as crystal_workers, SUM(CASE WHEN i.luxury_resource_id = 5 THEN m.workers ELSE 0 END) as sulfur_workers FROM helper_town AS t INNER JOIN helper_island AS i ON t.island_id == i.id INNER JOIN helper_user as u ON t.user_id = u.id INNER JOIN helper_sawmillworkers AS s ON s.level == i.wood_level INNER JOIN helper_mineworkers AS m ON m.level == i.luxury_level GROUP BY u.id, u.user_name ORDER BY " + order + " DESC"
    )
    results = cursor.fetchall()
    return results
