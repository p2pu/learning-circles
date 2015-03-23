from django.contrib import admin

# Register your models here.
from studygroups.models import Course, StudyGroup, StudyGroupSignup

class CourseAdmin(admin.ModelAdmin):
    pass

class StudyGroupAdmin(admin.ModelAdmin):
    pass

class StudyGroupSignupAdmin(admin.ModelAdmin):
    pass

admin.site.register(Course, CourseAdmin)
admin.site.register(StudyGroup, StudyGroupAdmin)
admin.site.register(StudyGroupSignup, StudyGroupSignupAdmin)
