from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Client, Rdv, Paiement

@login_required
def dashboard(request):
    context = {
        'total_clients': Client.objects.count(),
        'total_rdvs': Rdv.objects.count(),
        'total_paiements': Paiement.objects.count(),
    }
    return render(request, 'cabinet/dashboard.html', context)

@login_required
def clients_list(request):
    try:
        clients = Client.objects.all().order_by('-created_at')
        return render(request, 'cabinet/clients_list.html', {'clients': clients})
    except Exception as e:
        messages.error(request, f"Error loading clients: {str(e)}")
        return render(request, 'cabinet/clients_list.html', {'clients': []})

@login_required
def client_add(request):
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'cabinet/client_form.html')

@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'cabinet/client_detail.html', {'client': client})

@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'cabinet/client_form.html', {'client': client})

@login_required
def rdv_list(request):
    try:
        rdvs = Rdv.objects.all().select_related('client').order_by('-date', '-heure')
        return render(request, 'cabinet/rdv_list.html', {'rdvs': rdvs})
    except Exception as e:
        messages.error(request, f"Error loading appointments: {str(e)}")
        return render(request, 'cabinet/rdv_list.html', {'rdvs': []})

@login_required
def rdv_add(request):
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'cabinet/rdv_form.html')

@login_required
def rdv_detail(request, pk):
    rdv = get_object_or_404(Rdv, pk=pk)
    return render(request, 'cabinet/rdv_detail.html', {'rdv': rdv})

@login_required
def rdv_edit(request, pk):
    rdv = get_object_or_404(Rdv, pk=pk)
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'cabinet/rdv_form.html', {'rdv': rdv})

@login_required
def agenda(request):
    try:
        rdvs = Rdv.objects.all().select_related('client').order_by('date', 'heure')
        return render(request, 'cabinet/agenda.html', {'rdvs': rdvs})
    except Exception as e:
        messages.error(request, f"Error loading agenda: {str(e)}")
        return render(request, 'cabinet/agenda.html', {'rdvs': []})

@login_required
def paiements_list(request):
    try:
        paiements = Paiement.objects.all().select_related('client', 'rdv').order_by('-date_paiement')
        return render(request, 'cabinet/paiements_list.html', {'paiements': paiements})
    except Exception as e:
        messages.error(request, f"Error loading payments: {str(e)}")
        return render(request, 'cabinet/paiements_list.html', {'paiements': []})

@login_required
def paiement_add(request):
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'cabinet/paiement_form.html')

