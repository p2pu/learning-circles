from django.contrib import admin

# Register your models here.
from studygroups.models import Course, StudyGroup, StudyGroupSignup, Application

class StudyGroupSignupInline(admin.TabularInline):
    model = StudyGroupSignup

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
    list_display = ('name', 'contact_method', 'created_at')


admin.site.register(Course, CourseAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(StudyGroupSignup, StudyGroupSignupAdmin)
