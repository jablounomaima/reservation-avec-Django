# appointments/forms.py
from django.utils import timezone
from datetime import time
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Appointment, Pet  # ✅ Importe Pet
from django.contrib.auth.models import User
import re
from datetime import time  # Pour les TIME_CHOICES
# Créneaux horaires disponibles
# appointments/forms.py

from datetime import time
from django import forms
from django.utils import timezone
from .models import Appointment, Pet
import re

# Créneaux horaires
TIME_CHOICES = [
    (time(9, 0), '09:00'),
    (time(9, 30), '09:30'),
    (time(10, 0), '10:00'),
    (time(10, 30), '10:30'),
    (time(11, 0), '11:00'),
    (time(11, 30), '11:30'),
    (time(14, 0), '14:00'),
    (time(14, 30), '14:30'),
    (time(15, 0), '15:00'),
    (time(15, 30), '15:30'),
    (time(16, 0), '16:00'),
    (time(16, 30), '16:30'),
]

class AppointmentForm(forms.ModelForm):
    time = forms.ChoiceField(
        choices=[(t.strftime('%H:%M'), display) for t, display in TIME_CHOICES],
        label="Heure du rendez-vous",
        widget=forms.Select()
    )

    pet = forms.ModelChoiceField(
        queryset=None,
        label="Animal",
        empty_label="Sélectionnez un animal",
        help_text="Choisissez un animal parmi vos animaux enregistrés."
    )

    class Meta:
        model = Appointment
        fields = ['pet', 'service', 'date', 'time', 'phone', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'phone': forms.TextInput(attrs={'placeholder': '+212 6 12 34 56 78'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['pet'].queryset = Pet.objects.filter(owner=user)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Impossible de réserver un rendez-vous dans le passé.")
        return date

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Le numéro de téléphone est obligatoire.")
        phone = phone.strip()
        if not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone):
            raise forms.ValidationError("Numéro invalide. Ex: +212 6 12 34 56 78")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time_str = cleaned_data.get("time")

        if date and time_str:
            try:
                hour, minute = map(int, time_str.split(":"))
                time_obj = time(hour, minute)
                if Appointment.objects.filter(date=date, time=time_obj).exists():
                    raise forms.ValidationError("Ce créneau est déjà pris.")
            except ValueError:
                raise forms.ValidationError("Heure invalide.")
        return cleaned_data


# Formulaire d'inscription
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Adresse email",
        required=True,
        help_text="Requis pour la confirmation des rendez-vous."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# appointments/forms.py

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'species', 'breed', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }        