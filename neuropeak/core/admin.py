from django.contrib import admin
from .models import (
    Course, Assignment, Quiz, ChatMessage,
    QuizQuestion, QuizAttempt, QuizAnswer
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'lecturer')
    search_fields = ('name', 'lecturer__email')
    list_filter = ('lecturer',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'course__name')
    list_filter = ('course',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'course__name')
    list_filter = ('course',)

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz')
    search_fields = ('question_text', 'quiz__title')
    list_filter = ('quiz',)

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'score', 'attempted_at')
    search_fields = ('quiz__title', 'student__email')
    list_filter = ('quiz', 'student')

@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'student_answer', 'is_correct')
    search_fields = ('question__question_text', 'student_answer')
    list_filter = ('is_correct',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_message', 'created_at')
    search_fields = ('user__email', 'user_message')
    list_filter = ('user',)
