from django.contrib.auth.models import User
from django.db import models


class Script(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Stage(models.Model):
    name = models.CharField(max_length=255)
    order = models.IntegerField()
    script = models.ForeignKey(Script, on_delete=models.CASCADE)


class Task(models.Model):
    name = models.CharField(max_length=255)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)


class Parameter(models.Model):
    name = models.CharField(max_length=255)
    value = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
