from django import forms
from studygroups.models import StudyGroupSignup, Application
from localflavor.us.forms import USPhoneNumberField


class ApplicationForm(forms.ModelForm):
    mobile = USPhoneNumberField(required=False)

    def clean(self):
        cleaned_data = super(ApplicationForm, self).clean()
        contact_method = cleaned_data.get("contact_method")

        if contact_method == 'Email' and not cleaned_data.get('email'):
            self.add_error('email', "Please enter your email address or change your preferred contact method.")
        elif contact_method == 'Text' and not cleaned_data.get('mobile'):
            self.add_error('mobile', "Please enter your mobile number or change your preferred contact method.")
        elif contact_method == 'Phone' and not cleaned_data.get('mobile'):
            self.add_error('mobile', "Please enter your mobile number or change your preferred contact method.")

    class Meta:
        model = Application
        labels = {
            'mobile': 'What is your mobile number?',
            'contact_method': 'Preferred Method of Contact.',
            'computer_access': 'Do you have access to a computer outside of the library?',
            'goals': 'In one sentence, please explain your goals for taking this course.',
            'support': 'A successful study group requires the support of all of its members. How will you help your peers achieve their goals?',
            'study_group': 'Which course are you applying for? (by applying for a specific course, you agree to attend sessions at the specified time and location).',
        }
        exclude = ['accepted_at']


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
