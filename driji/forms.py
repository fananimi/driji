from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    identifier = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': _('Username or Email'),
            'class': 'form-control'
        }))
    password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Password'),
            'class': 'form-control'
        }))

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier')

        if '@' in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
        else:
            user = User.objects.filter(username__iexact=identifier).first()

        if not user:
            raise forms.ValidationError(_('User does not exists'))

        return user

    def clean(self):
        data = self.cleaned_data
        user = data.get('identifier')
        password = data.get('password')

        if user and password:
            authenticate_user = authenticate(
                username=user.username, password=password)

            if authenticate_user is None:
                err_message = _('Incorrect password')
                self._errors['password'] = self.error_class([err_message])

        return data

    def get_authenticate_user(self):
        data = self.cleaned_data
        username = data.get('identifier').username
        password = data.get('password')

        user = authenticate(username=username, password=password)

        return user
