from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import MaintenanceRequest, CATEGORY_CHOICES, STATUS_CHOICES, PRIORITY_CHOICES
from .forms import UserRegisterForm, MaintenanceRequestForm, StaffMaintenanceRequestForm


def get_tickets(user):
    tickets = MaintenanceRequest.objects.all()
    return tickets if user.is_staff else tickets.filter(user=user)


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'maintenance/home.html')
    tickets = get_tickets(request.user).filter(title__icontains=request.GET.get('q', ''))
    for field in ('category', 'status', 'priority'):
        if request.GET.get(field):
            tickets = tickets.filter(**{field: request.GET[field]})
    return render(request, 'maintenance/home.html', {
        'tickets': tickets.order_by('-date_reported'),
        'categories': CATEGORY_CHOICES,
        'statuses': STATUS_CHOICES,
        'priorities': PRIORITY_CHOICES,
    })

@login_required
def delete_request(request, pk):
    ticket = get_object_or_404(get_tickets(request.user), pk=pk)
    if request.method == 'POST':
        ticket.delete()
        return redirect('home')
    return render(request, 'maintenance/delete_request.html', {'maintenance_request': ticket})

def register_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())
        return redirect('home')
    return render(request, 'maintenance/register.html', {'form': form})


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect('home')
    return render(request, 'maintenance/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def submit_request(request):
    form = MaintenanceRequestForm(request.POST or None)
    if form.is_valid():
        form.instance.user = request.user
        form.save()
        return redirect('home')
    return render(request, 'maintenance/submit_request.html', {'form': form})


@login_required
def edit_request(request, pk):
    obj = get_object_or_404(get_tickets(request.user), pk=pk)
    form_class = StaffMaintenanceRequestForm if request.user.is_staff else MaintenanceRequestForm
    form = form_class(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'maintenance/edit_request.html', {'form': form})