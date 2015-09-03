from django.contrib import admin

# Register your models here.
from studygroups.models import Course, Location, StudyGroup, StudyGroupMeeting, Application, Reminder

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

class LocationAdmin(admin.ModelAdmin):
    pass

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'study_group', 'contact_method', 'created_at')

def reminder_course_title(obj):
    return obj.study_group.course.title

class ReminderAdmin(admin.ModelAdmin):
    list_display = (reminder_course_title, 'email_subject', 'sent_at')


admin.site.register(Course, CourseAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(StudyGroupMeeting, StudyGroupMeetingAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Reminder, ReminderAdmin)
