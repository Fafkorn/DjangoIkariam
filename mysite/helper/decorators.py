from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('helper:users')
        return view_func(request, *args, **kwargs)

    return wrapper_func


def admin_only():
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('Brak uprawnień')
        return wrapper_func
    return decorator
