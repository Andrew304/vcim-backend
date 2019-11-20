import operator

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from .models import Parameter, Script, Stage, Task


def authenticate_user(http_method):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if http_method == 'GET':
                user_email = request.GET.get('email')
                user_password = request.GET.get('password')
            else:
                user_email = request.POST.get('email')
                user_password = request.POST.get('password')

            if not user_email or not user_password:
                return JsonResponse({
                    'error': 'Missing field',
                }, status=400)

            user = authenticate(username=user_email, password=user_password)
            if user is None:
                return JsonResponse({'error': 'Incorrect email or password'}, status=401)
            request.user = user
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def register(request):
    user_email = request.POST.get('email')
    user_password = request.POST.get('password')

    if not user_email or not user_password:
        return JsonResponse({
            'error': 'Missing field'
        }, status=400)

    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        user = None

    if user:
        return JsonResponse({
            'error': 'This email already in use'
        }, status=400)

    user = User.objects.create_user(user_email, user_email, user_password)

    return JsonResponse({
        'user_id': user.id
    })


def login(request):
    user_email = request.POST.get('email')
    user_password = request.POST.get('password')

    if not user_email or not user_password:
        return JsonResponse({
            'error': 'Missing field',
        }, status=400)

    user = authenticate(username=user_email, password=user_password)
    if user is None:
        return JsonResponse({
            'error': 'Incorrect email or password',
        }, status=404)

    return JsonResponse({
        'user_id': user.id,
    })
