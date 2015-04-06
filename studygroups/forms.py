from django import forms
from studygroups.models import StudyGroupSignup, Application
from localflavor.us.forms import USPhoneNumberField


class ApplicationForm(forms.ModelForm):
    mobile = USPhoneNumberField(required=False)
    class Meta:
        model = Application
        labels = {
            'name': 'Please tell us what to call you',
            'mobile': 'What is your mobile number?',
            'contact_method': 'Please tell us how would you perfer us to contact us',
            'computer_access': 'Do you have normal everyday access to the computer?',
            'goals': 'Please tell what your learning goals are',
            'support': '',
        }
        widgets = {
            'study_groups': forms.CheckboxSelectMultiple,
        }


class SignupForm(forms.ModelForm):
    mobile = USPhoneNumberField(required=False)
    class Meta:
        model = StudyGroupSignup
        exclude = []
        widgets = {
            'study_group': forms.HiddenInput
        }


class EmailForm(forms.Form):
    study_group_id = forms.IntegerField(widget=forms.HiddenInput)
    subject = forms.CharField()
    body = forms.CharField(widget=forms.Textarea)
    sms_body = forms.CharField(max_length=160, widget=forms.Textarea)
