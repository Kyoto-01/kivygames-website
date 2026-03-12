"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import landing_page, login_view, register_view, logout_view, profile_view, delete_account_view
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', csrf_exempt(landing_page), name='home'),
    path('login/', csrf_exempt(login_view), name='login'),
    path('register/', csrf_exempt(register_view), name='register'),
    path('logout/', csrf_exempt(logout_view), name='logout'),
    path('profile/', csrf_exempt(profile_view), name='profile'),
    path('delete-account/', csrf_exempt(delete_account_view), name='delete_account'),
]
