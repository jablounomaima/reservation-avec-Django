# appointments/admin.py

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Pet, Appointment

# --- Inline : Afficher les rendez-vous dans le profil de l’animal ---
class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'phone')
    fields = ('service', 'date', 'time', 'status', 'notes', 'admin_notes', 'created_at')
    can_delete = False
    show_change_link = True


# --- Admin pour Pet (Animal) ---
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'owner', 'birth_date', 'created_at')
    list_filter = ('species', 'owner', 'created_at')
    search_fields = ('name', 'owner__username', 'phone')
    readonly_fields = ('created_at',)
    inlines = [AppointmentInline]  # Affiche tous les rendez-vous liés

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(owner=request.user)
        return qs

    # 🔹 Lien PDF dans le formulaire d’édition
    def historique_pdf(self, obj):
        if obj:
            url = reverse('appointments:pet_history_pdf', args=[obj.id])
            return format_html(
                '<a href="{}" class="button" target="_blank">📥 Télécharger l’historique (PDF)</a>',
                url
            )
        return "-"

    # 🔹 Ajoute le champ dans le formulaire
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            pet = Pet.objects.get(id=object_id)
            extra_context['historique_pdf'] = self.historique_pdf(pet)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # 🔹 Surcharge du template (optionnel)
    change_form_template = 'admin/appointments/pet/change_form.html'


# --- Admin pour Rendez-vous ---
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'service', 'date', 'time', 'phone', 'status', 'user', 'user_id', 'created_at')
    list_filter = ('status', 'date', 'service', 'pet__species', 'pet__owner')
    search_fields = ('pet__name', 'user__username', 'pet__owner__username', 'phone')
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')
    readonly_fields = ('created_at', 'updated_at', 'phone')

    # Actions rapides
    actions = ['mark_as_confirmed', 'mark_as_rejected', 'mark_as_pending']

    def user_id(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/">{}</a> ({})',
                obj.user.id,
                obj.user.id,
                obj.user.username
            )
        return "-"
    user_id.short_description = 'Identifiant utilisateur'
    user_id.admin_order_field = 'user'  

    @admin.action(description="✅ Confirmer les rendez-vous sélectionnés")
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"{updated} rendez-vous ont été confirmés.")

    @admin.action(description="❌ Refuser les rendez-vous sélectionnés")
    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} rendez-vous ont été refusés.")

    @admin.action(description="🔄 Remettre en attente")
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f"{updated} rendez-vous sont maintenant en attente.")

    # Affichage coloré du statut
    def status(self, obj):
        if obj.status == 'confirmed':
            return format_html('<span style="color: green; font-weight: bold;">✅ Confirmé</span>')
        elif obj.status == 'rejected':
            return format_html('<span style="color: red; font-weight: bold;">❌ Refusé</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">⏳ En attente</span>')
    status.short_description = 'Statut'


# --- Admin pour Utilisateur (custom) ---
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Désenregistrer l’admin par défaut
admin.site.unregister(User)

# Réenregistrer avec ajout de l’ID
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'user_phone', 'is_staff', 'is_active')
    ordering = ('id',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def user_phone(self, obj):
        last_appointment = Appointment.objects.filter(user=obj).order_by('-date').first()
        if last_appointment and last_appointment.phone:
            return format_html('<span style="color: #d9534f;">{}</span>', last_appointment.phone)
        return "-"
    user_phone.short_description = 'Téléphone (dernier rendez-vous)'
    user_phone.admin_order_field = 'appointment__date'
