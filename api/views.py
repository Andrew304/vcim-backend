import operator

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from yaml import Dumper, dump
import yamlordereddictloader
from collections import OrderedDict
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

@authenticate_user(http_method='GET')
def get_scripts(request):
    user_scripts = Script.objects.filter(owner=request.user)

    dict_user_scripts = {'Scripts':[]}
    if not user_scripts:
        return JsonResponse(dict_user_scripts)

    for script in user_scripts:
        dict_user_scripts['Scripts'].append({'id':script.id, 'title': script.title})

    return JsonResponse(dict_user_scripts)


@authenticate_user(http_method='POST')
def create_script(request):
    title_script = request.POST.get('title')

    if not title_script:
        return JsonResponse({
            'error': 'Missing field',
        }, status=400)

    try:
        script = Script.objects.get(title=title_script, owner=request.user)
    except Script.DoesNotExist:
        script = None

    if script is None:
        script = Script(title=title_script, owner=request.user)
        script.save()
    else:
        return JsonResponse({
            'error': 'This title is already in use',
        }, status=400)

    return JsonResponse({
        'script_id': script.id,
    })


@authenticate_user(http_method='POST')
def save_script(request, script_id):
    new_title_script = request.POST.get('title')

    if not new_title_script:
        return JsonResponse({
            'error': 'Missing field',
        }, status=400)

    try:
        script = Script.objects.get(id=script_id)
    except Script.DoesNotExist:
        return JsonResponse({
            'error': 'Incorrect script id',
        }, status=404)

    scripts_user = Script.objects.filter(owner=request.user)
    if scripts_user:
        try:
            script_equal_title = scripts_user.get(title=new_title_script)
        except Script.DoesNotExist:
            script_equal_title = None
        if script_equal_title and script.title != new_title_script:
            return JsonResponse({
                'error': 'This title is already in use',
            }, status=400)


    script.title = new_title_script
    script.save()

    return JsonResponse({
        'script_id': script.id,
    })


@authenticate_user(http_method='POST')
def export_script(request, script_id):
    try:
        script = Script.objects.get(id=script_id)
    except Script.DoesNotExist:
        return JsonResponse({
            'error': 'Incorrect script id',
        }, status=404)

    script_stages = Stage.objects.filter(script=script)
    if not script_stages:
        return JsonResponse({
            'error': 'This script doesnt have stages',
        }, status=404)

    dict_stages = {'stages' : []}
    sorted_script_stages = sorted(script_stages, key=operator.attrgetter('order'))
    for stage in sorted_script_stages:
        dict_stages['stages'].append(stage.name)
    all_stages = dump(dict_stages, Dumper=Dumper)

    dict_tasks = OrderedDict()
    for stage in sorted_script_stages:
        stage_tasks = Task.objects.filter(stage=stage)
        if stage_tasks:
            for task in stage_tasks:
                dict_tasks[task.name] = OrderedDict([('stage', stage.name)])
                task_parameters = Parameter.objects.filter(task=task)
                if task_parameters:
                    for parameter in task_parameters:
                        dict_tasks[task.name][parameter.name] = parameter.value

    all_tasks = dump(dict_tasks, Dumper=yamlordereddictloader.Dumper)
    script = all_stages + all_tasks

    return JsonResponse({
        'script': script,
    })

@authenticate_user(http_method='POST')
def remove_script(request, script_id):
    try:
        script = Script.objects.get(id=script_id)
    except Script.DoesNotExist:
        return JsonResponse({
            'error': 'Incorrect script id',
        }, status=404)

    script.delete()

    return JsonResponse({
        'script_id': script_id,
    })

@authenticate_user(http_method='GET')
def get_stages(request):
    script_id = request.GET.get('script_id')

    if not script_id:
        return JsonResponse({
            'error': 'Missing field',
        }, status=400)

    try:
        int(script_id)
    except ValueError:
        return JsonResponse({
            'error': 'Incorrect data type script id',
        }, status=400)

    try:
        script = Script.objects.get(id=script_id)
    except Script.DoesNotExist:
        return JsonResponse({
            'error': 'Incorrect script id',
        }, status=404)

    script_stages = Stage.objects.filter(script=script)

    dict_script_stages = {'Stages': []}
    if not script_stages:
        return JsonResponse(dict_script_stages)

    for stage in script_stages:
        dict_script_stages['Stages'].append({'id': stage.id, 'name': stage.name, 'order': stage.order})

    return JsonResponse(dict_script_stages)


@authenticate_user(http_method='POST')
def create_stage(request):
    name_stage = request.POST.get('name')
    order_stage = request.POST.get('order')
    script_id = request.POST.get('script_id')

    if not name_stage or not order_stage or not script_id:
        return JsonResponse({
            'error': 'Missing field',
        }, status=400)

    try:
        value = int(order_stage)
    except ValueError:
        return JsonResponse({
            'error': 'Incorrect data type order stage',
        }, status=400)

    if value < 0:
        return JsonResponse({
            'error': 'Order stage cant be negative',
        }, status=400)

    try:
        int(script_id)
    except ValueError:
        return JsonResponse({
            'error': 'Incorrect data type script id',
        }, status=400)

    try:
        script = Script.objects.get(id=script_id)
    except Script.DoesNotExist:
        return JsonResponse({
            'error': 'Incorrect script id',
        }, status=404)

    try:
        stage = Stage.objects.get(name=name_stage, script=script)
    except Stage.DoesNotExist:
        stage = None

    if stage is None:
        stage = Stage(name=name_stage, order=order_stage, script=script)
        stage.save()
    else:
        return JsonResponse({
            'error': 'This name is already in use',
        }, status=400)

    return JsonResponse({
        'stage_id': stage.id,
    })


@authenticate_user(http_method='POST')
def save_stage(request, stage_id):
    new_name_stage = request.POST.get('name')
    order_stage = request.POST.get('order')
    script_id = request.POST.get('script_id')

    if not new_name_stage or not order_stage or not script_id:
        return JsonResponse({
            'error': 'Missing field',
        }, status=400)

    try:
        value = int(order_stage)
    except ValueError:
        return JsonResponse({
            'error': 'Incorrect data type order stage',
        }, status=400)

    if value < 0:
        return JsonResponse({
            'error': 'Order stage cant be negative',
        }, status=400)

    try:
        int(script_id)
    except ValueError:
        return JsonResponse({
            'error': 'Incorrect data type script id',
        }, status=400)

    try:
        script = Script.objects.get(id=script_id)
    except Script.DoesNotExist:
        return JsonResponse({
            'error': 'Incorrect script id',
        }, status=404)

    try:
        stage = Stage.objects.get(id=stage_id)
    except Stage.DoesNotExist:
        return JsonResponse({
            'error': 'Incorrect stage id',
        }, status=404)

    script_stages = Stage.objects.filter(script=script)
    if script_stages:
        try:
            stages_equal_name = script_stages.filter(name=new_name_stage)
        except Stage.DoesNotExist:
            stages_equal_name = None
        if (stages_equal_name and stage not in stages_equal_name) or (stages_equal_name and stage in stages_equal_name and stages_equal_name.count() > 1):
            return JsonResponse({
                'error': 'This name is already in use',
            }, status=400)

    stage.name = new_name_stage
    stage.order = order_stage
    stage.script = script
    stage.save()

    return JsonResponse({
        'stage_id': stage.id,
    })


@authenticate_user(http_method='POST')
def remove_stage(request, stage_id):
    try:
        stage = Stage.objects.get(id=stage_id)
    except Stage.DoesNotExist:
        return JsonResponse({
            'error': 'Incorrect stage id',
        }, status=404)

    stage.delete()

    return JsonResponse({
        'stage_id': stage_id,
    })
