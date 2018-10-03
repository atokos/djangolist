from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            login(request, user)
            return redirect('homepage')
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'accounts/signup.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('homepage')
    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('homepage')

@login_required()
def profile_view(request):
    return render(request, 'accounts/profile.html')

