# appointments/views.py

from datetime import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentForm, CustomUserCreationForm

# appointments/views.py

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import weasyprint
from .models import Pet
# --- VUES PRINCIPALES ---

@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('-date', 'time')
    return render(request, 'appointments/list.html', {'appointments': appointments})


# appointments/views.py


# appointments/views.py

@login_required
def appointment_create(request):
    reschedule_id = request.GET.get('reschedule')
    original_appointment = None

    if reschedule_id:
        try:
            original_appointment = Appointment.objects.get(id=reschedule_id, user=request.user)
        except Appointment.DoesNotExist:
            messages.error(request, "Rendez-vous non trouvé.")
            return redirect('appointments:appointment_list')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)  # ✅ Passe user
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.status = 'pending'

            if Appointment.objects.filter(date=appointment.date, time=appointment.time).exists():
                form.add_error(None, "Ce créneau est déjà réservé.")
            else:
                appointment.save()

                # Envoi email
                send_mail(
                    subject=f"RDV en attente - {appointment.pet.name}",
                    message=f"Bonjour {request.user.username},\n\nVotre demande de rendez-vous pour {appointment.pet.name} a été envoyée.",
                    recipient_list=[request.user.email],
                    from_email='no-reply@veterinaire.local',
                    fail_silently=False,
                )

                if original_appointment:
                    original_appointment.delete()

                messages.success(request, "Votre demande a été envoyée (en attente de validation).")
                return redirect('appointments:appointment_list')
    else:
        initial_data = {}
        if original_appointment:
            initial_data = {
                'pet': original_appointment.pet.id,
                'service': original_appointment.service,
                'phone': original_appointment.phone,
                'notes': original_appointment.notes,
            }
        form = AppointmentForm(initial=initial_data, user=request.user)  # ✅ Passe user

    return render(request, 'appointments/create.html', {
        'form': form,
        'original_appointment': original_appointment
    })
@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Rendez-vous annulé.")
        return redirect('appointments:appointment_list')
    return render(request, 'appointments/confirm_delete.html', {'appointment': appointment})


# --- AUTHENTIFICATION ---

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f"Bienvenue {username} ! Votre compte a été créé.")
            return redirect('appointments:appointment_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'appointments/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Bonjour {username}, bienvenue !")
                return redirect('appointments:appointment_list')
            else:
                messages.error(request, "Identifiants invalides.")
    else:
        form = AuthenticationForm()
    return render(request, 'appointments/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('appointments:login')


# --- UTILITAIRE ---

def get_available_slots():
    """Retourne une liste de 5 créneaux disponibles"""
    from datetime import timedelta
    from django.utils import timezone

    today = timezone.now().date()
    available = []

    for days in range(1, 8):  # Prochains 7 jours
        current_date = today + timedelta(days=days)
        for t in [time(9,0), time(9,30), time(10,0), time(10,30),
                  time(11,0), time(11,30), time(14,0), time(14,30),
                  time(15,0), time(15,30), time(16,0), time(16,30)]:
            if not Appointment.objects.filter(date=current_date, time=t).exists():
                available.append({
                    'date': current_date,
                    'time': t,
                    'display': f"{current_date.strftime('%d/%m')} à {t.strftime('%H:%M')}"
                })
    return available[:5]




# appointments/views.py



@login_required
def pet_history_pdf(request, pet_id):
    # Autoriser l'accès si :
    # - L'utilisateur est le propriétaire, OU
    # - L'utilisateur est staff/superuser
    try:
        if request.user.is_staff:
            pet = Pet.objects.get(id=pet_id)  # Staff voit tous les animaux
        else:
            pet = Pet.objects.get(id=pet_id, owner=request.user)  # User normal → seulement ses animaux
    except Pet.DoesNotExist:
        raise Http404("Animal non trouvé.")

    appointments = pet.appointment_set.all().order_by('-date')

    html = render_to_string('appointments/history_pdf.html', {
        'pet': pet,
        'appointments': appointments,
        'now': timezone.now()
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="historique_{pet.name}.pdf"'

    weasyprint.HTML(string=html).write_pdf(response)
    return response






# appointments/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PetForm

@login_required
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            messages.success(request, f"Animal '{pet.name}' ajouté avec succès !")
            return redirect('appointments:appointment_create')
    else:
        form = PetForm()
    return render(request, 'appointments/add_pet.html', {'form': form})