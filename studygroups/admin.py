from django.contrib import admin

# Register your models here.
from studygroups.models import Course, StudyGroup, StudyGroupSignup, Application

class StudyGroupSignupInline(admin.TabularInline):
    model = StudyGroupSignup

class ApplicationInline(admin.TabularInline):
    model = Application.study_groups.through
    readonly_fields = ['user_name']
    def user_name(self, instance):
        return instance.application.name
    user_name.short_description = 'user name'

class StudyGroupAdmin(admin.ModelAdmin):
    inlines = [
        #StudyGroupSignupInline,
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
