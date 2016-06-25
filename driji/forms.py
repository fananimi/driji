# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User as AuthUser
from django.utils.translation import ugettext as _

from driji.models import PhoneBook, User

from zkcluster.models import Terminal

# from .models import Student, Grade


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
            user = AuthUser.objects.filter(email__iexact=identifier).first()
        else:
            user = AuthUser.objects.filter(username__iexact=identifier).first()

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


class StudentForm(forms.Form):
    # student information
    fullname = forms.CharField(
        label=_('full name'),
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': _('full name'),
            'class': 'form-control'
        })
    )
    gender = forms.ChoiceField(
        label=_('gender'),
        choices=User.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    phone_number = forms.CharField(
        label=_('phone number'),
        max_length=16,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    address = forms.CharField(
        label=_('address'),
        max_length=200,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )
    # parent information
    parent_fullname = forms.CharField(
        label=_('full name'),
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': _('full name'),
            'class': 'form-control'
        })
    )
    parent_gender = forms.ChoiceField(
        label=_('gender'),
        choices=User.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    parent_phone_number = forms.CharField(
        label=_('phone number'),
        max_length=16,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    parent_address = forms.CharField(
        label=_('address'),
        max_length=200,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )

    def is_phone_number_available(self, phone_number):
        phonebook = PhoneBook.objects.filter(phone_number__iexact=phone_number).first()
        if phonebook:
            return True
        return False

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if self.is_phone_number_available(phone_number):
            raise forms.ValidationError(_('this number already exits'))
        return phone_number

    def clean_parent_phone_number(self):
        phone_number = self.cleaned_data.get('parent_phone_number')
        if self.is_phone_number_available(phone_number):
            raise forms.ValidationError(_('this number already exits'))
        return phone_number

    def clean(self):
        cleaned_data = self.cleaned_data
        phone_number = cleaned_data.get('phone_number')
        parent_phone_number = cleaned_data.get('parent_phone_number')
        if phone_number and parent_phone_number:
            if phone_number.lower() == parent_phone_number.lower():
                err_message = _('phone number should be difference')
                self._errors['phone_number'] = self.error_class([err_message])
                self._errors['parent_phone_number'] = self.error_class([err_message])
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        # Parent Information
        parent_fullname = cleaned_data.get('parent_fullname')
        parent_gender = cleaned_data.get('parent_gender')
        parent_phone_number = cleaned_data.get('parent_phone_number')
        parent_address = cleaned_data.get('parent_address')

        new_parent = User.objects.create(
            fullname=parent_fullname,
            user_type=User.USER_PARENT,
            gender=parent_gender
        )
        PhoneBook.objects.create(
            address=parent_address,
            phone_number=parent_phone_number,
            driji_user=new_parent
        )

        # Student Information
        fullname = cleaned_data.get('fullname')
        gender = cleaned_data.get('gender')
        phone_number = cleaned_data.get('phone_number')
        address = cleaned_data.get('address')

        new_student = User.objects.create(
            fullname=fullname,
            user_type=User.USER_STUDENT,
            gender=gender,
            parent=new_parent
        )
        PhoneBook.objects.create(
            address=address,
            phone_number=phone_number,
            driji_user=new_student
        )

        return new_student
