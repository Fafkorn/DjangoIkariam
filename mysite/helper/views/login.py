from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login

from ..decorators import unauthenticated_user


@unauthenticated_user
def get_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('helper:users')
        else:
            messages.error(request, 'Nieprawidłowa nazwa lub hasło')

    context = {
        'title': 'Helper - Logowanie'}
    return render(request, 'helper/login.html', context)
