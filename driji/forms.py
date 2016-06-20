from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from zkcluster.models import Terminal

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

class ScanTerminalForm(forms.Form):
    ip = forms.CharField(
        label=_('IP Address'),
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': '192.168.200.1',
            'class': 'form-control',
        })
    )
    port = forms.IntegerField(
        label=_('Port'),
        widget=forms.TextInput(attrs={
            'value': 4370,
            'class': 'form-control',
        })
    )

    def clean_ip(self):
        ip = self.cleaned_data.get('ip')
        try:
            if self.instance.ip == ip:
                return ip
        except AttributeError:
            pass

        try:
            if self.instance.ip == ip:
                return ip
        except AttributeError:
            pass

        terminal = Terminal.objects.filter(ip__iexact=ip).first()
        if terminal:
            raise forms.ValidationError(_('IP already exists'))
        return ip

class AddTerminalForm(forms.ModelForm, ScanTerminalForm):
    serialnumber = forms.CharField(
        label=_('Serial Number'),
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': _('Serial number'),
            'class': 'form-control',
            'readonly': True
        })
    )
    name = forms.CharField(
        label=_('Name'),
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': _('Terminal name'),
            'class': 'form-control',
        })
    )

    class Meta:
        model = Terminal
        fields = ('ip', 'port', 'serialnumber', 'name')

    def __init__(self, *args, **kwargs):
        super(AddTerminalForm, self).__init__(*args, **kwargs)
        self.validate_name = False
        if len(args) > 1:
            self.validate_name = args[1].get('validate_name')

        self.fields['ip'].widget = forms.TextInput(attrs={
            'placeholder': _('IP Address'),
            'class': 'form-control',
            'readonly': True
        })
        self.fields['port'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True
        })

    def clean_serialnumber(self):
        serialnumber = self.cleaned_data.get('serialnumber')
        try:
            if self.instance.serialnumber == serialnumber:
                return serialnumber
        except AttributeError:
            pass

        terminal = Terminal.objects.filter(serialnumber__iexact=serialnumber).first()
        if terminal:
            raise forms.ValidationError(_('Serial number already exists'))
        return serialnumber

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.validate_name:
            if not name:
                raise forms.ValidationError(_('This field is required.'))
        return name

class EditTerminalForm(AddTerminalForm):
    def __init__(self, *args, **kwargs):
        super(EditTerminalForm, self).__init__(*args, **kwargs)

        self.fields['ip'].widget = forms.TextInput(attrs={
            'placeholder': _('IP Address'),
            'class': 'form-control'
        })
        self.fields['port'].widget = forms.TextInput(attrs={
            'class': 'form-control'
        })
