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
            'contact_method': 'Preferred Method of Contact.',
            'computer_access': 'Do you have access to a computer outside of the library?',
            'goals': 'In one sentence, please explain your goals for taking this course.',
            'support': 'A successful study group requires the support of all of its members. How will you help your peers achieve their goals?',
            'study_groups': 'Which course are you applying for? (by applying for a specific course, you agree to attend sessions at the specified time and location).',
        }
        widgets = {
            'study_groups': forms.CheckboxSelectMultiple,
        }
        fields = '__all__'


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
