from django.contrib import admin

# Register your models here.
from studygroups.models import Course, StudyGroup, StudyGroupSignup, Application

class CourseAdmin(admin.ModelAdmin):
    pass

class StudyGroupSignupInline(admin.TabularInline):
    model = StudyGroupSignup

class StudyGroupAdmin(admin.ModelAdmin):
    inlines = [StudyGroupSignupInline]

class StudyGroupSignupAdmin(admin.ModelAdmin):
    pass

class ApplicationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Course, CourseAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(StudyGroupSignup, StudyGroupSignupAdmin)
