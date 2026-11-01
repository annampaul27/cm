from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # user requests
    path('submit/', views.submit_request, name='submit_request'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    path('edit/<int:pk>/', views.edit_request, name='edit_request'),
    path('delete/<int:pk>/', views.delete_request, name='delete_request'),

    # staff
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/update/<int:pk>/', views.staff_update_status, name='staff_update_status'),
    path('staff/delete/<int:pk>/', views.staff_delete_request, name='staff_delete_request'),
]