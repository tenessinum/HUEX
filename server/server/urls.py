from django.contrib import admin
from django.urls import path
from huex import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main),
    path('post', views.post_telemetry),  # For telemerty post
    path('get', views.get_info),  # For telemetry recive
    path('send', views.send_command),  # For sending commands from web
    path('delete', views.delete)  # For deleting drones
]
