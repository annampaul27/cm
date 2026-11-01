from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import MaintenanceRequest, CATEGORY_CHOICES, STATUS_CHOICES
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'category', 'location', 'priority']
class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['status']
class RequestFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[('', 'All Status')] + STATUS_CHOICES, required=False)
    category = forms.ChoiceField(choices=[('', 'All Categories')] + CATEGORY_CHOICES, required=False)