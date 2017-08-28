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
from studygroups.models import TeamInvitation

class ApplicationInline(admin.TabularInline):
    model = Application

class StudyGroupAdmin(admin.ModelAdmin):
    inlines = [ ApplicationInline ]

class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'page_slug')
    inlines = [ TeamMembershipInline ]

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'study_group', 'email', 'mobile', 'created_at')

def reminder_course_title(obj):
    return obj.study_group.course.title

class ReminderAdmin(admin.ModelAdmin):
    list_display = (reminder_course_title, 'email_subject', 'sent_at')


class CourseAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(CourseAdmin, self).get_queryset(request)
        return qs.active()

    def created_by(course):
        def display_user(user):
            return u'{} {}'.format(user.first_name, user.last_name)
        return display_user(course.created_by) if course.created_by else 'P2PU'

    def email(course):
        return course.created_by.email if course.created_by else '-'

    def learning_circles(course):
        return course.studygroup_set.active().count()

    list_display = ('title', 'provider', 'on_demand', 'topics', learning_circles, created_by, email)


admin.site.register(Course, CourseAdmin)
admin.site.register(Activity)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(StudyGroupMeeting)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamInvitation)
