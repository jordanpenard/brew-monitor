from django.urls import path
from . import views

urlpatterns = [
    path("storage/sensor/add_data", views.add_sensor_data, name="add_sensor_data"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path("sensors/", views.sensor_list, name="sensor_list"),
    path("sensors/<int:sensor_id>/", views.sensor_detail, name="sensor_detail"),
    path("datapoints/<int:datapoint_id>/delete/", views.delete_datapoint, name="delete_datapoint"),
    path("projects/<int:project_id>/delete/", views.delete_project, name="delete_project"),
    path("sensors/<int:sensor_id>/delete/", views.delete_sensor, name="delete_sensor"),
    path("projects/create/", views.create_project, name="create_project"),
    path("sensors/create/", views.create_sensor, name="create_sensor"),
    path("projects/<int:project_id>/edit/", views.edit_project, name="edit_project"),
    path("sensors/<int:sensor_id>/edit/", views.edit_sensor, name="edit_sensor"),
    path("projects/<int:project_id>/attach_sensor/", views.attach_sensor_to_project, name="attach_sensor_to_project"),
    path('ajax_datatable/', views.DatatableView.as_view(), name="ajax_datatable"),
]
