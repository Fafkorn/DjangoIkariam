from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from ..forms import CreateUserForm
from django.contrib import messages


def get_register(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid() and is_key_correct(request.POST['key'], form):
            form.save()
            messages.success(request, 'Zarejestrowano pomyślnie')
            return redirect('helper:login')

    context = {
        'form': form,
        'title': 'Helper - Rejestracja'
    }
    return render(request, 'helper/register.html', context)


def is_key_correct(key: str, form):
    if key == '123':
        return True
    form.add_error('password1', 'Niepoprawny klucz')
    return False

