from django.contrib import admin
from .models import Quiz, Question, QuizAttempt

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'created_at')
    inlines = [QuestionInline]

class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'date_taken')  # removed 'total'

admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
