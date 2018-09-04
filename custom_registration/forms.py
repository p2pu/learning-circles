# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import ugettext as _
from django.forms import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from studygroups.models import Profile


class SignupForm(UserCreationForm):
    newsletter = forms.BooleanField(required=False, label=_('Subscribe to newsletter?'))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        username = cleaned_data.get('email')
        if User.objects.filter(username__iexact=username).exists():
            self.add_error('email', _('A user with that email address already exists.'))
        return cleaned_data

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'newsletter']


class CustomPasswordResetForm(PasswordResetForm):
    """ Use case insensitive email address when searching for users """

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError(_("There is no user registered with the specified email address!"))

        return email
