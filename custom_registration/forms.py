# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import gettext as _
from django.forms import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe

from studygroups.models import Profile


newsletter_label = _('P2PU can contact me')
newsletter_help_text = _('Join our mailing list to learn about upcoming events, new courses, and news from the community. (Approximately six emails/year)')

class SignupForm(UserCreationForm):
    communication_opt_in = forms.BooleanField(required=False, initial=False, label=newsletter_label, help_text=newsletter_help_text)

    consent_opt_in = forms.BooleanField(required=True, initial=False, label=mark_safe(_('I consent to P2PU storing my data and accept the <a href="https://www.p2pu.org/en/terms/">terms of service</a>')), help_text=_('P2PU values your privacy and will never sell your data.'))

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
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'consent_opt_in', 'communication_opt_in']


class CustomPasswordResetForm(PasswordResetForm):
    """ Use case insensitive email address when searching for users """

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError(_("There is no user registered with the specified email address!"))

        return email

class UserForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, help_text=mark_safe(_('If you’d like to change the address affiliated with your account, please contact <a href="mailto:thepeople@p2pu.org">thepeople@p2pu.org</a>')))

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'contact_url', 'city', 'country', 'place_id', 'region', 'latitude', 'longitude', 'communication_opt_in']
        labels = {
            'avatar': _('Profile photo'),
            'bio': _('Short bio (max 500 characters)'),
            'contact_url': _('Contact URL'),
            'city': _('City'),
            'communication_opt_in': newsletter_label,
        }
        placeholders = {
            'contact_url': _("Twitter, LinkedIn, website, etc.")
        }
        help_texts = {
             'contact_url': _('Where can potential team members find your contact information? i.e. Staff page, Twitter, personal website, etc.'),
             'communication_opt_in': newsletter_help_text,
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows':5, 'cols':10}),
            'latitude': forms.HiddenInput,
            'longitude': forms.HiddenInput,
            'place_id': forms.HiddenInput,
            'country': forms.HiddenInput,
            'region': forms.HiddenInput,
        }
