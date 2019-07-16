from django.contrib import admin
from django.urls import path
from huex import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main),
    path('m', views.mobile),
    path('post', views.post_telemetry),  # For telemerty post
    path('get', views.get_info),  # For telemetry recive
    path('send', views.send_command),  # For sending commands from web
    path('delete', views.delete),  # For deleting drones
    path('set', views.set_field),  # For changing map
    path('set_color', views.set_color),  # For changing map
    path('ask_taxi', views.ask_taxi),  # For asking taxi
    path('get_dist', views.get_dist),  # For counting distance
    path('get_busy_points', views.get_busy_points),
    path('ip_status', views.ip_status)
]
