import random
import string

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..decorators import admin_only
from ..models import RegisterKey


@login_required(login_url='helper:login')
@admin_only()
def get_key_manager(request):
    context = {}

    if request.method == 'POST':
        register_key = RegisterKey()
        register_key.key = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        register_key.save()
        context['key'] = register_key.key
    return render(request, 'helper/key_manager.html', context)




