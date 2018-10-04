from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.views import View

from .forms import SignupForm, EditEmailForm


class AccountChangeEmailView(View):
    template_name = 'accounts/change_email.html'

    def post(self, request):
        form = EditEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')

    def get(self, request):
        form = EditEmailForm(instance=request.user)
        return render(request, self.template_name, {'form': form})


class AccountProfileView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        return render(request, self.template_name)


class AccountChangePasswordView(View):
    template_name = 'accounts/change_password.html'

    def post(self, request):
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')

    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, self.template_name, {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            login(request, user)
            return redirect('homepage')
    else:
        form = SignupForm()
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


@login_required()
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('homepage')

