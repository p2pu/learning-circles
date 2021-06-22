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
    communication_opt_in = forms.BooleanField(required=False, initial=False, label=_('P2PU can contact me.'), help_text=_('Joining the community comes with an expectation that you would like to learn about upcoming events, new features, and updates from around the world. If you do not want to receive any of these messages, uncheck this box.'))
    interested_in_learning = forms.CharField(required=False, label=_('What are you interested in learning?'))

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
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'interested_in_learning', 'communication_opt_in']


class CustomPasswordResetForm(PasswordResetForm):
    """ Use case insensitive email address when searching for users """

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError(_("There is no user registered with the specified email address!"))

        return email

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'contact_url', 'city', 'country', 'place_id', 'region', 'latitude', 'longitude', 'communication_opt_in']
        labels = {
            'avatar': _('Profile photo'),
            'bio': _('Short bio (max 500 characters)'),
            'contact_url': _('Contact URL'),
            'city': _('City'),
            'communication_opt_in': _('Receive announcements'),
        }
        placeholders = {
            'contact_url': _("Twitter, LinkedIn, website, etc.")
        }
        help_texts = {
             'contact_url': _('Where can potential team members find your contact information? i.e. Staff page, Twitter, personal website, etc.'),
             'communication_opt_in': _('Check this box if you want to receive updates from the P2PU community about upcoming events and gatherings.')
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows':5, 'cols':10}),
            'latitude': forms.HiddenInput,
            'longitude': forms.HiddenInput,
            'place_id': forms.HiddenInput,
            'country': forms.HiddenInput,
            'region': forms.HiddenInput,
        }
