from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from .models import MaintenanceRequest
from .forms import UserRegisterForm, MaintenanceRequestForm, StatusUpdateForm, RequestFilterForm


def home(request):
    return render(request, 'maintenance/home.html')


# ---------- FILTER HELPER ----------

def _apply_request_filters(request, queryset):
    filter_form = RequestFilterForm(request.GET or None)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        category = filter_form.cleaned_data.get('category')
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category=category)
    return queryset, filter_form


# ---------- AUTHENTICATION ----------

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()          # create the user
            login(request, user)        # log them in straight away
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'maintenance/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()      # checks username + password
            login(request, user)        # creates the session
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'maintenance/login.html', {'form': form})


def logout_view(request):
    logout(request)                     # ends the session
    return redirect('home')


# ---------- USER CRUD (own requests only) ----------

@login_required
def submit_request(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)   # don't save yet
            obj.user = request.user         # attach logged-in user
            obj.save()
            return redirect('my_requests')
    else:
        form = MaintenanceRequestForm()
    return render(request, 'maintenance/submit_request.html', {'form': form})


@login_required
def my_requests(request):
    requests, filter_form = _apply_request_filters(
        request, MaintenanceRequest.objects.filter(user=request.user))
    return render(request, 'maintenance/my_requests.html',
                  {'requests': requests, 'filter_form': filter_form})


@login_required
def request_detail(request, pk):
    obj = get_object_or_404(MaintenanceRequest, pk=pk)
    if not (request.user == obj.user or request.user.is_staff):
        return redirect('home')
    return render(request, 'maintenance/request_detail.html', {'maintenance_request': obj})


@login_required
def edit_request(request, pk):
    obj = get_object_or_404(MaintenanceRequest, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('my_requests')
    else:
        form = MaintenanceRequestForm(instance=obj)
    return render(request, 'maintenance/edit_request.html',
                  {'form': form, 'maintenance_request': obj})


@login_required
def delete_request(request, pk):
    obj = get_object_or_404(MaintenanceRequest, pk=pk, user=request.user)
    if request.method == 'POST':
        obj.delete()
    return redirect('my_requests')


# ---------- STAFF ONLY ----------

@login_required
#@user_passes_test(lambda u: u.is_staff)
def staff_dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied
    requests, filter_form = _apply_request_filters(request, MaintenanceRequest.objects.all())
    return render(request, 'maintenance/staff_dashboard.html',
                  {'requests': requests, 'filter_form': filter_form})


@login_required
#@user_passes_test(lambda u: u.is_staff)
def staff_update_status(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    obj = get_object_or_404(MaintenanceRequest, pk=pk)
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('staff_dashboard')
    else:
        form = StatusUpdateForm(instance=obj)
    return render(request, 'maintenance/staff_update_status.html',
                  {'form': form, 'maintenance_request': obj})


@login_required
@require_POST
def staff_delete_request(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    obj = get_object_or_404(MaintenanceRequest, pk=pk)
    obj.delete()
    return redirect('staff_dashboard')