from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import UserPreference


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = {
            'username',
            'email',
            'password1',
            'password2'
        }

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class EditEmailForm(UserChangeForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = {
            'email',
            'password',
         }


class AccountSetPreferencesForm(forms.ModelForm):

    class Meta:
        model = UserPreference
        fields = {
            'language',
        }
