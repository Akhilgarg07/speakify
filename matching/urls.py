from django.urls import path
from . import views

app_name = 'matching'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update_online_status/', views.update_online_status, name='update_online_status'),
    path('find_match/', views.find_match, name='find_match'),
    # path('stop_search/', views.stop_search, name='stop_search'),
]
