from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)

    def _str_(self):
        return f"{self.code} - {self.name}"

class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=225)
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    option4 = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=100)

    def _str_(self):
        return self.question_text

class ExamSettings(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    instructions = models.TextField(default='Answer all questions carefully.')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=10)
    questions_per_page = models.IntegerField(default=2)

    def _str_(self):
        return f"{self.subject.name} - {self.title}"

class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamSettings, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} - {self.exam.subject.name} - {self.score}/{self.total}"

class Student(models.Model):
    registration_number = models.CharField(max_length=50, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def _str_(self):
        return self.registration_number

class StudentExam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamSettings, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    allowed_retake = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'exam']

    def _str_(self):
        return f"{self.user.username} - {self.exam.subject.name} - Completed: {self.completed}"