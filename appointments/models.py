# appointments/models.py

from django.db import models
from django.contrib.auth.models import User

# Choix pour les champs
PET_CHOICES = [
    ('dog', 'Chien'),
    ('cat', 'Chat'),
    ('other', 'Autre'),
]

SERVICE_CHOICES = [
    ('vaccination', 'Vaccination'),
    ('checkup', 'Consultation'),
    ('deworming', 'Traitement antiparasitaire'),
    ('surgery', 'Chirurgie'),
    ('dental', 'Soins dentaires'),
]

STATUS_CHOICES = [
    ('pending', 'En attente'),
    ('confirmed', 'Confirmé'),
    ('rejected', 'Refusé'),
]


# --- Modèle Pet (Animal) ---
class Pet(models.Model):
    name = models.CharField("Nom", max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    species = models.CharField(
        "Espèce",
        max_length=10,
        choices=PET_CHOICES
    )
    breed = models.CharField("Race", max_length=100, blank=True, null=True)
    birth_date = models.DateField("Date de naissance", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animaux"
        unique_together = ('name', 'owner')  # Un utilisateur ne peut pas avoir deux animaux avec le même nom

    def __str__(self):
        return f"{self.name} ({self.get_species_display()}) - {self.owner.username}"


# --- Modèle Appointment (Rendez-vous) ---
class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name="Animal")
    service = models.CharField("Service", max_length=20, choices=SERVICE_CHOICES)
    date = models.DateField("Date du rendez-vous")
    time = models.TimeField("Heure du rendez-vous")
    phone = models.CharField("Téléphone", max_length=15, help_text="Ex: +212 6 12 34 56 78")
    notes = models.TextField("Remarques", blank=True, null=True)

    status = models.CharField(
        "Statut",
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    admin_notes = models.TextField(
        "Notes admin",
        blank=True,
        null=True,
        help_text="Message envoyé à l'utilisateur si le RDV est refusé"
    )

    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        unique_together = ['date', 'time']  # Un créneau horaire ne peut pas être réservé deux fois
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.pet.name} - {self.get_service_display()} le {self.date}"