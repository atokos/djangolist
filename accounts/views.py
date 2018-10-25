from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.urls import reverse
from django.views import View
from django.utils import translation

from .models import UserPreference
from .forms import SignupForm, EditEmailForm, AccountSetPreferencesForm


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
        user = request.user
        preferences = UserPreference.objects.get(user=user)
        return render(request, self.template_name, {'preferences': preferences})


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


class AccountSetPreferencesView(View):

    def get(self, request):
        preferences = UserPreference.objects.get(user=request.user)
        form = AccountSetPreferencesForm(instance=preferences)
        return render(request, 'accounts/preferences.html', {'form': form})

    def post(self, request):
        preferences = UserPreference.objects.get(user=request.user)
        form = AccountSetPreferencesForm(data=request.POST, instance=preferences)
        if form.is_valid():
            language_code = form.cleaned_data.get('language', 'en')
            form.save()
            set_language(request, language_code)
            return redirect(reverse('accounts:profile'))
        return render(request, 'accounts/preferences.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            preferences = UserPreference()
            preferences.user = user
            preferences.save()
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
            users = UserPreference.objects.filter(user=user)
            if users:
                language_code = users[0].language
                set_language(request, language_code)
            else:
                preferences = UserPreference()
                preferences.user = user
                preferences.save()
                language_code = UserPreference.objects.filter(user=user)
                set_language(request, language_code)
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
        reset_language(request)
        return redirect('homepage')


def set_currency(request):
    if request.method == 'POST':
        currency = request.POST.get('currency')
        print(currency)
        request.session['currency'] = currency
        return redirect(reverse('homepage'))


def set_language(request, language_code):
    translation.activate(language_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = language_code


def reset_language(request):
    if translation.LANGUAGE_SESSION_KEY in request.session:
        request.session[translation.LANGUAGE_SESSION_KEY] = 'en'

