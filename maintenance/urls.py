from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('submit/', views.submit_request, name='submit_request'),
    path('edit/<int:pk>/', views.edit_request, name='edit_request'),
    path('delete/<int:pk>/', views.delete_request, name='delete_request'),
]