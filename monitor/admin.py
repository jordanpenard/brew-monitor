from django.contrib import admin
from .models import Project, Sensor, Datapoint

admin.site.register(Project)
admin.site.register(Sensor)
admin.site.register(Datapoint)
