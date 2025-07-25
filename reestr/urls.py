from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('dashboard/edit_contractor/', views.podryad_profile_edit, name='podryad_profile_edit'),
    path('register/driver/', views.driver_signup, name='driver_signup'),
    path('register/podryad/', views.podryad_signup, name='podryad_signup'),
    path('profile/change_credentials/', views.user_change_credentials, name='user_change_credentials'),
    path('profile/contractor_change_credentials/', views.contractor_change_credentials, name='contractor_change_credentials'),
    path('export/excel/', views.export_flights_to_excel, name='export_excel'),
]