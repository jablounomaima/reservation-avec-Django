from django.db import models

# Create your models here.
# accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biographie")
    location = models.CharField(max_length=100, blank=True, verbose_name="Localisation")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Photo de profil"
    )
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Téléphone")

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

# Signal pour créer automatiquement un profil quand un utilisateur est créé
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal pour sauvegarder le profil quand l'utilisateur est sauvegardé
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()