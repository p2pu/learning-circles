from django.contrib import admin

# Register your models here.
from studygroups.models import Course
from studygroups.models import StudyGroup 
from studygroups.models import StudyGroupMeeting 
from studygroups.models import Application 
from studygroups.models import Reminder 
from studygroups.models import Activity
from studygroups.models import Organizer
from studygroups.models import Facilitator
from studygroups.models import Team
from studygroups.models import TeamMembership

class ApplicationInline(admin.TabularInline):
    model = Application

class StudyGroupAdmin(admin.ModelAdmin):
    inlines = [ ApplicationInline ]

class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership

class TeamAdmin(admin.ModelAdmin):
    inlines = [ TeamMembershipInline ]

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'study_group', 'email', 'mobile', 'created_at')

def reminder_course_title(obj):
    return obj.study_group.course.title

class ReminderAdmin(admin.ModelAdmin):
    list_display = (reminder_course_title, 'email_subject', 'sent_at')


admin.site.register(Course)
admin.site.register(Activity)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(StudyGroupMeeting)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(Organizer)
admin.site.register(Facilitator)
admin.site.register(Team, TeamAdmin)
