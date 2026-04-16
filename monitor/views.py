import json
import time

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ajax_datatable.views import AjaxDatatableView

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import formats
from django.template.loader import render_to_string
from django.contrib import messages

from .models import Datapoint, Project, Sensor

# Helper for admin checks
def is_admin(user):
    return user.is_authenticated and user.is_staff
admin_required = user_passes_test(is_admin)

@csrf_exempt
@require_POST
def add_sensor_data(request):
    try:
        data = json.loads(request.body)
        sensor_id = data.get("sensor_id")
        angle = data.get("angle")
        temperature = data.get("temperature")
        battery = data.get("battery")
        secret = data.get("secret")

        sensor = get_object_or_404(Sensor, pk=sensor_id)

        if not sensor.secret == secret:
            return JsonResponse({"status": "error", "message": "Invalid sensor secret"}, status=403)

        # Find the active project for the sensor, if any
        project = Project.objects.filter(active_sensor=sensor).first()

        datapoint = Datapoint.objects.create(
            sensor=sensor,
            project=project,
            angle=float(angle),
            temperature=float(temperature),
            battery=float(battery),
        )

        return JsonResponse({
            "created": [{
                "sensor_id": datapoint.sensor.id,
                "project_id": datapoint.project.id if datapoint.project else None,
                "timestamp": int(datapoint.timestamp.timestamp()),
                "angle": str(datapoint.angle),
                "temperature": str(datapoint.temperature),
                "battery": str(datapoint.battery)
            }]
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Sensor.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Sensor not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def project_list(request):
    projects = Project.objects.order_by("-id").all()
    return render(request, "project_list.html", {"projects": projects})

def data_graph(datapoints):
    x = []
    y = []
    y2 = []

    for dp in datapoints:
        x.append(dp.timestamp.isoformat())
        y.append(dp.temperature)
        y2.append(dp.angle)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=x, y=y, name="Temperature"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=x, y=y2, name="Angle"),
        secondary_y=True,
    )

    fig.update_xaxes(title_text="Timestamp")

    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
    fig.update_yaxes(title_text="Angle (°)", secondary_y=True)

    return fig.to_html(full_html=False, include_plotlyjs='cdn')

class DatatableView(AjaxDatatableView):

    model = Datapoint
    title = 'Datapoints'
    initial_order = [["timestamp", "desc"], ]
    #length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    #search_values_separator = '+'

    column_defs = [
        {'name': 'timestamp', 'title': "When", },
        {'name': 'angle', 'title': "Angle (°)", },
        {'name': 'temperature', 'title': "Temperature (°C)", },
        {'name': 'battery', 'title': "Battery (V)", },
        {'name': 'tools', 'title': '', 'placeholder': True, 'searchable': False, 'orderable': False, 'visible': False, 'width': '31px'},
    ]

    def get_column_defs(self, request):
        column_defs = self.column_defs
        if self.request.user.is_authenticated:
            for col in column_defs:
                if col['name'] == 'tools':
                    col['visible'] = True
        
        return column_defs

    def get_initial_queryset(self, request=None):

        project_id = request.REQUEST.get('project_id', None)
        sensor_id = request.REQUEST.get('sensor_id', None)

        queryset = self.model.objects.all()
        if project_id:
            queryset = queryset.filter(project=int(project_id))
        elif sensor_id:
            queryset = queryset.filter(sensor=int(sensor_id))

        return queryset

    def customize_row(self, row, obj):
        project_id = self.request.POST.get('project_id', "")
        sensor_id = self.request.POST.get('sensor_id', "")

        # Format the date using a specific Django format or string
        row['timestamp'] = formats.date_format(obj.timestamp, "Y-m-d  H:i:s")
        row['tools'] = render_to_string("delete_datapoint.html", {"id": obj.id, "project": project_id, "sensor": sensor_id}, request=self.request)

def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    datapoints = Datapoint.objects.filter(project=project).order_by("-timestamp")

    available_sensors = Sensor.objects.all()

    return render(request, "project_detail.html", {
        "project": project,
        "data_graph": data_graph(datapoints),
        "available_sensors": available_sensors,
    })

def sensor_list(request):
    sensors = Sensor.objects.all()
    return render(request, "sensor_list.html", {
        "sensors": sensors,
    })

def sensor_detail(request, sensor_id):
    sensor = get_object_or_404(Sensor, pk=sensor_id)
    datapoints = Datapoint.objects.filter(sensor=sensor).order_by("-timestamp")
    previous_projects = Project.objects.filter(datapoints__sensor=sensor).distinct().order_by("-id")
    return render(request, "sensor_detail.html", {
        "sensor": sensor, 
        "previous_projects": previous_projects,
        "data_graph": data_graph(datapoints),
    })

@login_required()
@require_POST
def delete_datapoint(request, datapoint_id):
    datapoint = get_object_or_404(Datapoint, pk=datapoint_id)
    datapoint.delete()

    next_project = request.GET.get('project', None)
    next_sensor = request.GET.get('sensor', None)
    
    if next_project:
        return redirect("project_detail", project_id=next_project)
    if next_sensor:
        return redirect("sensor_detail", sensor_id=next_sensor)
    return redirect("/")

@login_required()
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user == project.owner:
        project.delete()
    else:
        messages.error(request, "You can't delete someone else's project")
    return redirect("project_list")

@admin_required
@require_POST
def delete_sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, pk=sensor_id)
    if request.user == sensor.owner:
        sensor.delete()
    else:
        messages.error(request, "You can't delete someone else's sensor")
    return redirect("sensor_list")

@login_required()
@require_POST
def create_project(request):
    name = request.POST["name"]
    owner = request.user
    Project.objects.create(name=name, owner=owner)
    return redirect("project_list")

@login_required()
@require_POST
def create_sensor(request):
    name = request.POST["name"]
    secret = request.POST["secret"]
    owner_id = request.POST["owner"]
    owner = get_object_or_404(User, pk=owner_id)
    max_battery = float(request.POST.get("max_battery", 4.0))
    min_battery = float(request.POST.get("min_battery", 2.0))
    Sensor.objects.create(name=name, secret=secret, owner=owner, max_battery=max_battery, min_battery=min_battery)
    return redirect("sensor_list")

@login_required()
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.name = request.POST["name"]
        owner_id = request.POST["owner"]
        project.owner = get_object_or_404(User, pk=owner_id)
        project.save()
        return redirect("project_list")
    users = User.objects.all()
    return render(request, "edit_project.html", {"project": project, "users": users})

@login_required()
def edit_sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, pk=sensor_id)
    if request.method == "POST" :
        sensor.name = request.POST["name"]
        sensor.secret = request.POST["secret"]
        owner_id = request.POST["owner"]
        sensor.owner = get_object_or_404(User, pk=owner_id)
        sensor.max_battery = float(request.POST.get("max_battery", 4.0))
        sensor.min_battery = float(request.POST.get("min_battery", 2.0))
        sensor.save()
        return redirect("sensor_list")
    users = User.objects.all()
    return render(request, "edit_sensor.html", {"sensor": sensor, "users": users})

@login_required()
@require_POST
def attach_sensor_to_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    sensor_id = request.POST.get("sensor_id") # Can be None to detach
    brew_id = request.GET.get("brew", None)
    if sensor_id:
        current_active_project = Project.objects.filter(active_sensor_id=sensor_id).first()
        if current_active_project:
            current_active_project.active_sensor = None
            current_active_project.save()
        sensor = get_object_or_404(Sensor, pk=sensor_id)
        project.active_sensor = sensor
    else:
        project.active_sensor = None
    project.save()

    if brew_id:
        return redirect("edit_brew", pk=brew_id)
    else:
        return redirect("project_detail", project_id=project.id)
    