from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from localflavor.us.forms import USPhoneNumberField

import pytz

from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import StudyGroup
from studygroups.models import StudyGroupMeeting
from studygroups.models import Feedback


class ApplicationForm(forms.ModelForm):
    mobile = USPhoneNumberField(required=False)

    def clean(self):
        cleaned_data = super(ApplicationForm, self).clean()
        contact_method = cleaned_data.get("contact_method")

        if contact_method == Application.EMAIL and not cleaned_data.get('email'):
            self.add_error('email', _('Please enter your email address or change your preferred contact method.'))
        elif contact_method == Application.TEXT and not cleaned_data.get('mobile'):
            self.add_error('mobile', _('Please enter your mobile number or change your preferred contact method.'))

    class Meta:
        model = Application
        labels = {
            'mobile': _('What is your mobile number?'),
            'contact_method': _('Preferred Method of Contact.'),
            'computer_access': _('Can you bring your own laptop to the Learning Circle?'),
            'goals': _('In one sentence, please explain your goals for taking this course.'),
            'support': _('A successful study group requires the support of all of its members. How will you help your peers achieve their goals?'),
        }
        exclude = ['accepted_at']
        widgets = {'study_group': forms.HiddenInput} 


class MessageForm(forms.ModelForm):
    class Meta:
        model = Reminder
        exclude = ['study_group_meeting', 'created_at', 'sent_at']
        widgets = {'study_group': forms.HiddenInput} 


class StudyGroupForm(forms.ModelForm):
    start_date = forms.SplitDateTimeField(input_time_formats=['%I:%M %p'])
    end_date = forms.SplitDateTimeField(input_time_formats=['%I:%M %p'])
    timezone = forms.ChoiceField(choices=zip(pytz.common_timezones, pytz.common_timezones))

    def clean(self):
        cleaned_data = super(StudyGroupForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if end_date < start_date:
            msg = _('Start date needs to be after end date')
            self.add_error('end_date', msg)

        # TODO - Make sure days are the same

    class Meta:
        model = StudyGroup
        fields = [
            'course',
            'location',
            'location_details',
            'facilitator',
            'start_date',
            'end_date',
            'duration',
            'timezone',
        ]


class FacilitatorForm(forms.ModelForm):
    username = forms.EmailField(required=True, label=_('Email'))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


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
            'feedback': _('Write your Learning Circle summary here (this will be sent out to the Learning Circle with next week\'s reminder message). Include the plus delta, feedback from the intervention, and anything else you want included.'),
            'attendance': _('How many people attended?'),
            'reflection': _('Just between us, anything else you want to add? (Use this for reflections, concerns, and anything else you want us to know to help improve Learning Circles).'),
            'rating': _('Overall, how would you say this week went?')
        }
        widgets = {'study_group_meeting': forms.HiddenInput} 
