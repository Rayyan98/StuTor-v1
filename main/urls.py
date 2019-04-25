"""TMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from django.conf.urls import url


app_name = "main"

urlpatterns = [
	path('', views.homepage,name='homepage'),

	path('login/', views.login_request),

	path('register/student/', views.register_student),
	path('register/broker/', views.register_broker),
	path('register/', views.register),
	path('logout/', views.logout_request),
	path('register/successful/', views.register_successful, name = 'register_successful'),
	path('register/tutor/', views.register_tutor, name = 'register_tutor'),

	path('password_change/', views.password_change, name='password_change'),
	
	path('account/', views.view_account ,name='view_account'),
	path('account/edit/', views.edit_account , name = 'account_edit'),

	path('chat/', views.index , name = 'index'),
	path('chat/<room_name>/', views.room, name='room'),
	
]

