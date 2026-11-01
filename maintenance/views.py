from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.urls import reverse
from django.utils.http import urlencode
from .models import MaintenanceRequest
from .forms import (
    UserRegisterForm,
    MaintenanceRequestForm,
    StaffMaintenanceRequestForm,
    TicketFilterForm,
)


def home(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            return redirect('login')
        return render(request, 'maintenance/home.html')

    queryset = MaintenanceRequest.objects.all()
    if not request.user.is_staff:
        queryset = queryset.filter(user=request.user)

    if request.method == 'POST':
        if request.POST.get('action') != 'delete':
            return redirect('home')
        ticket = get_object_or_404(queryset, pk=request.POST.get('ticket_id'))
        ticket.delete()
        return _redirect_to_filtered_home(request.POST, prefix='filter_')

    filter_form = TicketFilterForm(request.GET)
    if filter_form.is_valid():
        query = filter_form.cleaned_data['q'].strip()
        if query:
            for term in query.split():
                search_filter = (
                    Q(title__icontains=term)
                    | Q(description__icontains=term)
                    | Q(location__icontains=term)
                    | Q(category__icontains=term)
                    | Q(priority__icontains=term)
                    | Q(status__icontains=term)
                )
                search_filter |= (
                    Q(user__username__icontains=term)
                    | Q(user__email__icontains=term)
                )
                if term.isdigit():
                    search_filter |= Q(pk=term)
                queryset = queryset.filter(search_filter)
        if filter_form.cleaned_data['category']:
            queryset = queryset.filter(category=filter_form.cleaned_data['category'])
        if filter_form.cleaned_data['status']:
            queryset = queryset.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data['priority']:
            queryset = queryset.filter(priority=filter_form.cleaned_data['priority'])

    tickets = queryset.select_related('user').order_by('-date_reported')
    return render(request, 'maintenance/home.html', {
        'tickets': tickets,
        'filter_form': filter_form,
    })


def _redirect_to_filtered_home(data, prefix=''):
    filters = {
        key: data.get(f'{prefix}{key}', '')
        for key in ('q', 'category', 'status', 'priority')
        if data.get(f'{prefix}{key}')
    }
    url = reverse('home')
    if filters:
        url = f'{url}?{urlencode(filters)}'
    return redirect(url)


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
            return redirect('home')
    else:
        form = MaintenanceRequestForm()
    return render(request, 'maintenance/submit_request.html', {'form': form})


@login_required
def edit_request(request, pk):
    queryset = MaintenanceRequest.objects.all()
    if not request.user.is_staff:
        queryset = queryset.filter(user=request.user)
    obj = get_object_or_404(queryset, pk=pk)
    form_class = StaffMaintenanceRequestForm if request.user.is_staff else MaintenanceRequestForm
    if request.method == 'POST':
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = form_class(instance=obj)
    return render(request, 'maintenance/edit_request.html',
                  {'form': form, 'maintenance_request': obj})
