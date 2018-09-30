from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


def profile_view(request):
    return render(request, 'accounts/profile.html')


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
