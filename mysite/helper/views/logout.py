from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url='helper:login')
def get_logout(request):
    logout(request)
    messages.info(request, 'Wylogowano pomyślnie')
    return redirect('helper:login')
