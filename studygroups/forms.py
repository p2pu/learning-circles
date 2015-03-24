from django import forms
from studygroups.models import StudyGroupSignup

class SignupForm(forms.ModelForm):
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
