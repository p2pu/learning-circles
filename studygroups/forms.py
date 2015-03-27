from django import forms
from studygroups.models import StudyGroupSignup
from localflavor.us.forms import USPhoneNumberField

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
