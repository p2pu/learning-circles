from django.contrib import admin

# Register your models here.
from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import Profile
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation


class ApplicationInline(admin.TabularInline):
    model = Application


class StudyGroupAdmin(admin.ModelAdmin):
    inlines = [ApplicationInline]

    list_display = ['course', 'city', 'facilitator', 'start_date', 'day', 'signup_open']


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    raw_id_fields = ("user",)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'page_slug', 'members')
    inlines = [TeamMembershipInline]

    def members(self, obj):
        return obj.teammembership_set.active().count()


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'study_group', 'email', 'mobile', 'created_at')


def reminder_course_title(obj):
    return obj.study_group.course.title


class ReminderAdmin(admin.ModelAdmin):
    list_display = (reminder_course_title, 'email_subject', 'sent_at')


class StudyGroupInline(admin.TabularInline):
    model = StudyGroup
    fields = ('venue_name', 'city', 'start_date', 'day')
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CourseAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(CourseAdmin, self).get_queryset(request)
        return qs.active()

    def created_by(course):
        def display_user(user):
            return '{} {}'.format(user.first_name, user.last_name)
        return display_user(course.created_by) if course.created_by else 'P2PU'

    def email(course):
        return course.created_by.email if course.created_by else '-'

    def learning_circles(course):
        return course.studygroup_set.active().count()

    def listed(course):
        return not course.unlisted
    listed.boolean = True

    list_display = ('id', 'title', 'provider', 'on_demand', 'topics', learning_circles, created_by, email, listed, 'license')
    exclude = ('deleted_at',)
    inlines = [StudyGroupInline]
    search_fields = ['title', 'provider', 'topics', 'created_by__email', 'license']


class ProfileAdmin(admin.ModelAdmin):
    def user(profile):
        return " ".join([profile.user.first_name, profile.user.last_name])
    list_display = [user, 'mailing_list_signup', 'communication_opt_in']
    search_fields = ['user__email']


admin.site.register(Course, CourseAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(Meeting)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamInvitation)
admin.site.register(Profile, ProfileAdmin)
