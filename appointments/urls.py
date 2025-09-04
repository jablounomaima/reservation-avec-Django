from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.home, name='home'), 
    path('list', views.appointment_list, name='appointment_list'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('delete/<int:pk>/', views.appointment_delete, name='appointment_delete'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),  # voir ci-dessous
        path('pet/<int:pet_id>/history.pdf', views.pet_history_pdf, name='pet_history_pdf'),
          # appointments/urls.py

path('pet/add/', views.add_pet, name='add_pet'),  # ✅ Ajouté

]
