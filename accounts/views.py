from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def signup_view(request):

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # TODO log user in
            return redirect('homepage')
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'accounts/signup.html', context)


def login_view(request):
    if request.method == 'POST':
        pass

    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    return render(request, 'accounts/logout.html')


def profile_view(request):
    return render(request, 'accounts/profile.html')

