from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login after registration
            return redirect('home')  # Adjust redirect as needed
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
