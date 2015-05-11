from django.contrib import admin

# Register your models here.
from studygroups.models import Course, StudyGroup, Application, Reminder

class ApplicationInline(admin.TabularInline):
    model = Application

class StudyGroupAdmin(admin.ModelAdmin):
    inlines = [
        ApplicationInline,
    ]

class StudyGroupSignupAdmin(admin.ModelAdmin):
    pass

class CourseAdmin(admin.ModelAdmin):
    pass

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'study_group', 'contact_method', 'created_at')

class ReminderAdmin(admin.ModelAdmin):
    pass


admin.site.register(Course, CourseAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Reminder, ReminderAdmin)
