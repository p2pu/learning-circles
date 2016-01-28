from django import forms
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth.models import User

from localflavor.us.forms import USPhoneNumberField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, MultiField

import pytz, datetime, json

from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import StudyGroup
from studygroups.models import StudyGroupMeeting
from studygroups.models import Feedback


class ApplicationForm(forms.ModelForm):
    COMPUTER_ACCESS = (
        ('Both', 'Both'),
        ('Just a laptop', 'Just a laptop'),
        ('Just headphones', 'Just headphones'),
        ('Neither', 'Neither'),
    )
    DIGITAL_LITERACY_CHOICES = (
        ('0', _(u'Can\'t do')), 
        ('1', _(u'Need help doing')),
        ('2', _(u'Can do with difficulty')), 
        ('3', _(u'Can do')),
        ('4', _(u'Expert (can teach others)')),
    )

    mobile = USPhoneNumberField(required=False, label=_('Phone Number for SMS'), help_text=_('if no email available (currently US numbers only)'))
    computer_access = forms.ChoiceField(
        choices=COMPUTER_ACCESS,
        label=_('Can you bring a laptop and headphones to the Learning Circle each week?')
    )
    goals = forms.CharField(
        label=_('In one sentence, please explain your goals for taking this course.')
    )
    support = forms.CharField(
        label=_('A successful study group requires the support of all of its members. How will you help your peers achieve their goals?')
    )

    send_email = forms.ChoiceField(label=_('Send an email'), choices=DIGITAL_LITERACY_CHOICES)
    delete_spam = forms.ChoiceField(label=_('Delete spam email'), choices=DIGITAL_LITERACY_CHOICES)
    search_online = forms.ChoiceField(label=_('Find stuff online using Google'), choices=DIGITAL_LITERACY_CHOICES)
    browse_video = forms.ChoiceField(label=_('Watch a video on Youtube'), choices=DIGITAL_LITERACY_CHOICES)
    online_shopping = forms.ChoiceField(label=_('Fill out an application form or buy something online'), choices=DIGITAL_LITERACY_CHOICES)
    mobile_apps = forms.ChoiceField(label=_('Use a mobile app'), choices=DIGITAL_LITERACY_CHOICES)
    web_safety = forms.ChoiceField(label=_('Evaluate whether a website is safe/can be trusted'), choices=DIGITAL_LITERACY_CHOICES)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'study_group', 'name', 'email', 'mobile', 'goals', 'support', 'computer_access',
            Fieldset(
                _(u'How comfortable are you doing the following tasks?'),
                'send_email', 'delete_spam', 'search_online', 'browse_video', 'online_shopping', 'mobile_apps', 'web_safety'
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))
        super(ApplicationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        signup_questions = {}
        questions = ['computer_access', 'goals', 'support', 'send_email', 'delete_spam', 'search_online', 'browse_video', 'online_shopping', 'mobile_apps', 'web_safety']
        for question in questions:
            signup_questions[question] = self.cleaned_data[question]
        self.instance.signup_questions = json.dumps(signup_questions)
        return super(ApplicationForm, self).save(commit)

    def clean(self):
        cleaned_data = super(ApplicationForm, self).clean()
        contact_method = cleaned_data.get("contact_method")

        if not cleaned_data.get('mobile') and not cleaned_data.get('email'):
            self.add_error('email', _('Please provide your email address or a US mobile number to sign up.'))

    class Meta:
        model = Application
        fields = ['study_group', 'name', 'email', 'mobile']
        widgets = {'study_group': forms.HiddenInput} 


class MessageForm(forms.ModelForm):
    class Meta:
        model = Reminder
        exclude = ['study_group_meeting', 'created_at', 'sent_at']
        widgets = {'study_group': forms.HiddenInput} 


class StudyGroupForm(forms.ModelForm):
    meeting_time = forms.TimeField(input_formats=['%I:%M %p'])
    weeks = forms.IntegerField(min_value=1, label=_('How many weeks will your learning circle run?'))
    timezone = forms.ChoiceField(choices=zip(pytz.common_timezones, pytz.common_timezones))

    def __init__(self, *args, **kwargs):
        super(StudyGroupForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['weeks'].initial = self.instance.studygroupmeeting_set.active().count()

    def save(self, commit=True):
        self.instance.end_date = self.cleaned_data['start_date'] + datetime.timedelta(weeks=self.cleaned_data['weeks'] - 1)
        return super(StudyGroupForm, self).save(commit)

    class Meta:
        model = StudyGroup
        fields = [
            'course',
            'venue_name',
            'venue_address',
            'venue_details',
            'venue_website',
            'facilitator',
            'start_date',
            'weeks',
            'meeting_time',
            'duration',
            'timezone',
            'image',
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
