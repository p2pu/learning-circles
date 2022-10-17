from django.contrib import admin
from django import forms

# Register your models here.
from studygroups.models import Course
from studygroups.models import TopicGuide
from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import Profile
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import Announcement
from studygroups.models import FacilitatorGuide


class ApplicationInline(admin.TabularInline):
    model = Application
    exclude = ['deleted_at']

    def get_queryset(self, request):
        return super().get_queryset(request).active()



class StudyGroupAdmin(admin.ModelAdmin):
    inlines = [ApplicationInline]
    list_display = ['course', 'city', 'facilitators', 'start_date', 'day', 'signup_open', 'uuid']
    exclude = ['deleted_at']
    search_fields = ['course__title', 'uuid', 'city', 'facilitator__user__first_name', 'facilitator__user__email']
    raw_id_fields = ['course', 'created_by']

    def facilitators(self, study_group):
        return study_group.facilitators_display()

    def get_queryset(self, request):
        return super().get_queryset(request).active()


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    raw_id_fields = ["user"]
    exclude = ['deleted_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.active()


class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'page_slug', 'members']
    inlines = [TeamMembershipInline]

    def members(self, obj):
        return obj.teammembership_set.active().count()


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'study_group', 'email', 'mobile', 'created_at']
    search_fields = ['name', 'email', 'mobile']
    exclude = ['deleted_at']

    def get_queryset(self, request):
        return super().get_queryset(request).active()


def reminder_course_title(obj):
    return obj.study_group.name


class ReminderAdmin(admin.ModelAdmin):
    list_display = [reminder_course_title, 'email_subject', 'sent_at']
    raw_id_fields = ['study_group', 'study_group_meeting']



class FacilitatorGuideForm(forms.ModelForm):
    class Meta:
        model = FacilitatorGuide
        fields = [
            'study_group',
            'title',
            'caption',
            'link',
        ]


class FacilitatorGuideAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'study_group', 'course']
    list_display = ['title', 'course', 'user']

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during foo creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = FacilitatorGuideForm
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


    def save_model(self, request, obj, form, change):
        if obj.study_group:
            obj.course = obj.study_group.course
            obj.user = obj.study_group.created_by
        super().save_model(request, obj, form, change)


class StudyGroupInline(admin.TabularInline):
    model = StudyGroup
    fields = ['id', 'venue_name', 'city', 'start_date', 'day']
    readonly_fields = fields


    def get_queryset(self, request):
        return super().get_queryset(request).active()

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CourseAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
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

    list_display = ['id', 'title', 'provider', 'keywords', learning_circles, created_by, email, listed, 'license']
    exclude = ['deleted_at']
    inlines = [StudyGroupInline]
    search_fields = ['title', 'provider', 'keywords', 'created_by__email', 'license']
    raw_id_fields = ['created_by']


class ProfileAdmin(admin.ModelAdmin):
    def user(profile):
        return " ".join([profile.user.first_name, profile.user.last_name])
    list_display = [user, 'communication_opt_in']
    search_fields = ['user__email']


class MeetingAdmin(admin.ModelAdmin):
    raw_id_fields = ['study_group']
    exclude = []


admin.site.register(Course, CourseAdmin)
admin.site.register(TopicGuide)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamInvitation)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Announcement)
admin.site.register(FacilitatorGuide, FacilitatorGuideAdmin)
