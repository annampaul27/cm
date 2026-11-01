from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    MaintenanceRequest,
    CATEGORY_CHOICES,
    PRIORITY_CHOICES,
    STATUS_CHOICES,
)
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'category', 'location', 'priority']


class StaffMaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'category', 'location', 'priority', 'status']


class TicketFilterForm(forms.Form):
    q = forms.CharField(label='Search', required=False)
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + CATEGORY_CHOICES,
        required=False,
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + STATUS_CHOICES,
        required=False,
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + PRIORITY_CHOICES,
        required=False,
    )