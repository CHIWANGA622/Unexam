from django.contrib import admin
from django.contrib.auth.models import User
from .models import Question, Result, Student, ExamSettings, StudentExam, Subject

class StudentAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            user = User.objects.create_user(
                username=obj.registration_number,
                password='chuo123'
            )
            obj.user = user
        super().save_model(request, obj, form, change)

class StudentExamAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'completed', 'allowed_retake']
    list_editable = ['allowed_retake']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'question_text']
    list_filter = ['subject']

admin.site.register(Subject)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Result)
admin.site.register(Student, StudentAdmin)
admin.site.register(ExamSettings)
admin.site.register(StudentExam, StudentExamAdmin)