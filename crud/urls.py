from django.urls import path, include
from . import views
from . views import AuthView
from django.contrib.auth import views as auth_views
from django.contrib import admin


urlpatterns = [
    path("", views.home, name="base"),
    path("signup/", AuthView, name="signup"),   
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("accounts/", include("django.contrib.auth.urls")),

    path('gender/list', views.gender_list, name='gender_list'),    
    path('gender/add', views.add_gender, name='add_gender'),
    path('gender/edit/<int:genderId>', views.edit_gender, name='edit_gender'),  
    path('gender/delete/<int:genderId>', views.delete_gender, name='delete_gender'),  

    path('user/list/', views.user_list, name='user_list'), 
    path('user/add/', views.add_user, name='add_user'),   
    path('user/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]
