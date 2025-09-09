# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm


# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import UserRegisterForm

def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, "Vous êtes déjà connecté.")
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Crée l'utilisateur
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            # ✅ Passe 'request' en premier argument à authenticate()
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {username} !')
                return redirect('home')
            else:
                # En théorie, cela ne devrait jamais arriver après un form.save() valide
                messages.error(request, "Erreur lors de la connexion automatique. Veuillez vous connecter manuellement.")
                return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # ✅ Passe 'request' à authenticate() → requis par AxesBackend
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.info(request, f"Connecté en tant que {username}.")
                return redirect('home')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Déconnexion réussie.")
    return redirect('login')


def home_view(request):
    return render(request, 'accounts/home.html', {'user': request.user})