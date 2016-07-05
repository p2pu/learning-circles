from django.contrib import admin

# Register your models here.
from studygroups.models import Course, StudyGroup, StudyGroupMeeting, Application, Reminder, Activity
from studygroups.models import Organizer
from studygroups.models import Facilitator

class ApplicationInline(admin.TabularInline):
    model = Application

class StudyGroupAdmin(admin.ModelAdmin):
    inlines = [
        ApplicationInline,
    ]

class StudyGroupMeetingAdmin(admin.ModelAdmin):
    pass

class StudyGroupSignupAdmin(admin.ModelAdmin):
    pass

class CourseAdmin(admin.ModelAdmin):
    pass

class ActivityAdmin(admin.ModelAdmin):
    pass

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'study_group', 'email', 'mobile', 'created_at')

def reminder_course_title(obj):
    return obj.study_group.course.title

class ReminderAdmin(admin.ModelAdmin):
    list_display = (reminder_course_title, 'email_subject', 'sent_at')

class OrganizerAdmin(admin.ModelAdmin):
    pass

class FacilitatorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Course, CourseAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(StudyGroupMeeting, StudyGroupMeetingAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(Facilitator, FacilitatorAdmin)
