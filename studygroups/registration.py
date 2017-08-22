from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import ugettext as _
from django.forms import ValidationError

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError(_("There is no user registered with the specified email address!"))

        return email
