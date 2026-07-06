from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Course, Section, Lesson, Prerequisite, QuestionBank, 
    MultipleChoice, Assignment, Enrollment, Progress, 
    AssignmentSubmission, QuizAttempt
)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Configuration', {'fields': ('role',)}),
    )

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'difficulty', 'status', 'created_at')
    list_filter = ('status', 'difficulty')
    search_fields = ('title', 'instructor__username')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(User, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Section)
admin.site.register(Lesson)
admin.site.register(Prerequisite)
admin.site.register(QuestionBank)
admin.site.register(MultipleChoice)
admin.site.register(Assignment)
admin.site.register(Enrollment)
admin.site.register(Progress)
admin.site.register(AssignmentSubmission)
admin.site.register(QuizAttempt)

from .models import LearningPath, LearningPathCourse, CourseAnnouncement, LessonComment
admin.site.register(LearningPath)
admin.site.register(LearningPathCourse)
admin.site.register(CourseAnnouncement)
admin.site.register(LessonComment)