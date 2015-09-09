from django import forms
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import StudyGroup
from studygroups.models import StudyGroupMeeting
from studygroups.models import Feedback
from localflavor.us.forms import USPhoneNumberField


class ApplicationForm(forms.ModelForm):
    mobile = USPhoneNumberField(required=False)

    def clean(self):
        cleaned_data = super(ApplicationForm, self).clean()
        contact_method = cleaned_data.get("contact_method")

        if contact_method == Application.EMAIL and not cleaned_data.get('email'):
            self.add_error('email', "Please enter your email address or change your preferred contact method.")
        elif contact_method == Application.TEXT and not cleaned_data.get('mobile'):
            self.add_error('mobile', "Please enter your mobile number or change your preferred contact method.")

    class Meta:
        model = Application
        labels = {
            'mobile': 'What is your mobile number?',
            'contact_method': 'Preferred Method of Contact.',
            'computer_access': 'Can you bring your own laptop to the Learning Circle?',
            'goals': 'In one sentence, please explain your goals for taking this course.',
            'support': 'A successful study group requires the support of all of its members. How will you help your peers achieve their goals?',
        }
        exclude = ['accepted_at']
        widgets = {'study_group': forms.HiddenInput} 


class MessageForm(forms.ModelForm):
    class Meta:
        model = Reminder
        exclude = ['study_group_meeting', 'created_at', 'sent_at']
        widgets = {'study_group': forms.HiddenInput} 


class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ['location_details', 'start_date', 'end_date', 'duration']


class StudyGroupMeetingForm(forms.ModelForm):
    meeting_time = forms.SplitDateTimeField(input_time_formats=['%I:%M %p'])
    class Meta:
        model = StudyGroupMeeting
        fields = ['meeting_time', 'study_group']
        widgets = {'study_group': forms.HiddenInput} 


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ['']
        labels = {
            'feedback': 'Write your Learning Circle summary here (this will be sent out to the Learning Circle with next week\'s reminder message). Include the plus delta, feedback from the intervention, and anything else you want included.',
            'attendance': 'How many people attended?',
            'reflection': 'Just between us, anything else you want to add? (Use this for reflections, concerns, and anything else you want us to know to help improve Learning Circles).',
            'rating': 'Overall, how would you say this week went?'
        }
        widgets = {'study_group_meeting': forms.HiddenInput} 
