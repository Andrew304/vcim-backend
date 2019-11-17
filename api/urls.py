from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),

    path('script', views.get_scripts),
    path('script/create', views.create_script),
    path('script/<int:script_id>/save', views.save_script),
    path('script/<int:script_id>/export', views.export_script),
    path('script/<int:script_id>/remove', views.remove_script),

    path('stage', views.get_stages),
    path('stage/create', views.create_stage),
    path('stage/<int:stage_id>/save', views.save_stage),
    path('stage/<int:stage_id>/remove', views.remove_stage),

    path('task', views.get_tasks),
    path('task/create', views.create_task),
    path('task/<int:task_id>/save', views.save_task),
    path('task/<int:task_id>/remove', views.remove_task),

    path('parameter', views.get_parameters),
    path('parameter/create', views.create_parameter),
    path('parameter/<int:parameter_id>/save', views.save_parameter),
    path('parameter/<int:parameter_id>/remove', views.remove_parameter),
]
