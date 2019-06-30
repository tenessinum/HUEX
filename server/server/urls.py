from django.contrib import admin
from django.urls import path
from huex import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main),
    path('get/', views.get_info)
]
