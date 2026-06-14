from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Question, Result, Student, ExamSettings, StudentExam, Subject
from django.utils import timezone

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect("dashboard")
            else:
                return redirect("exam_list")
        else:
            return render(request, "login.html", {"error": "Invalid registration number or password!"})
    return render(request, "login.html")

@login_required(login_url='/login/')
def dashboard_view(request):
    if not request.user.is_staff:
        return redirect("exam_list")
    total_students = Student.objects.count()
    total_exams = ExamSettings.objects.count()
    total_results = Result.objects.count()
    total_subjects = Subject.objects.count()
    recent_results = Result.objects.all().order_by('-date')[:10]
    subjects = Subject.objects.all()
    return render(request, "dashboard.html", {
        "total_students": total_students,
        "total_exams": total_exams,
        "total_results": total_results,
        "total_subjects": total_subjects,
        "recent_results": recent_results,
        "subjects": subjects,
    })

@login_required(login_url='/login/')
def exam_list_view(request):
    now = timezone.now()
    exams = ExamSettings.objects.all()
    student_exams = StudentExam.objects.filter(user=request.user)
    completed_exams = [se.exam.id for se in student_exams if se.completed and not se.allowed_retake]
    return render(request, "exam_list.html", {
        "exams": exams,
        "completed_exams": completed_exams,
    })

@login_required(login_url='/login/')
def exam_view(request, exam_id):
    exam = ExamSettings.objects.get(id=exam_id)
    now = timezone.now()
    if now < exam.start_time:
        return render(request, "exam_closed.html", {"message": "This exam has not started yet!"})
    if now > exam.end_time:
        return render(request, "exam_closed.html", {"message": "This exam time is over!"})
    student_exam, created = StudentExam.objects.get_or_create(user=request.user, exam=exam)
    if student_exam.completed and not student_exam.allowed_retake:
        return redirect("my_results")
    questions = list(Question.objects.filter(subject=exam.subject))
    total_questions = len(questions)
    page = int(request.GET.get('page', 1))
    total_pages = (total_questions + exam.questions_per_page - 1) // exam.questions_per_page
    start = (page - 1) * exam.questions_per_page
    end = start + exam.questions_per_page
    current_questions = questions[start:end]
    if request.method == "POST":
        for q in current_questions:
            answer = request.POST.get(str(q.id))
            if answer:
                request.session[f'answer_{exam_id}_{q.id}'] = answer
        if 'submit' in request.POST:
            return redirect(f'/confirm/{exam_id}/')
        elif page < total_pages:
            return redirect(f'/exam/{exam_id}/?page={page + 1}')
    saved_answers = {}
    for q in questions:
        saved_answers[q.id] = request.session.get(f'answer_{exam_id}_{q.id}', '')
    return render(request, "exam.html", {
        "questions": current_questions,
        "page": page,
        "total_pages": total_pages,
        "title": exam.title,
        "instructions": exam.instructions,
        "saved_answers": saved_answers,
        "exam_id": exam_id,
        "duration": exam.duration_minutes * 60,
    })

@login_required(login_url='/login/')
def confirm_submit_view(request, exam_id):
    exam = ExamSettings.objects.get(id=exam_id)
    questions = list(Question.objects.filter(subject=exam.subject))
    if request.method == "POST":
        score = 0
        answers = []
        for q in questions:
            answer = request.session.get(f'answer_{exam_id}_{q.id}', '')
            is_correct = answer == q.correct_answer
            if is_correct:
                score += 1
            answers.append({
                'question': q.question_text,
                'your_answer': answer,
                'correct_answer': q.correct_answer,
                'is_correct': is_correct,
            })
        Result.objects.create(user=request.user, exam=exam, score=score, total=len(questions))
        student_exam = StudentExam.objects.get(user=request.user, exam=exam)
        student_exam.completed = True
        student_exam.allowed_retake = False
        student_exam.save()
        request.session[f'last_answers_{exam_id}'] = answers
        request.session[f'last_score_{exam_id}'] = score
        request.session[f'last_total_{exam_id}'] = len(questions)
        for q in questions:
            request.session.pop(f'answer_{exam_id}_{q.id}', None)
        return redirect('my_results')
    return render(request, "confirm_submit.html", {"exam_id": exam_id})

@login_required(login_url='/login/')
def my_results_view(request):
    results = Result.objects.filter(user=request.user).order_by('-date')
    return render(request, "my_results.html", {"results": results})

@login_required(login_url='/login/')
def results_view(request):
    if request.user.is_staff:
        results = Result.objects.all().order_by('-date')
    else:
        results = Result.objects.filter(user=request.user).order_by('-date')
    return render(request, "all_results.html", {"results": results})

@login_required(login_url='/login/')
def change_password_view(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if not request.user.check_password(old_password):
            return render(request, "change_password.html", {"error": "Current password is incorrect!"})
        if new_password != confirm_password:
            return render(request, "change_password.html", {"error": "New passwords do not match!"})
        if len(new_password) < 6:
            return render(request, "change_password.html", {"error": "Password must be at least 6 characters!"})
        request.user.set_password(new_password)
        request.user.save()
        return render(request, "change_password.html", {"success": "Password changed successfully! Please login again."})
    return render(request, "change_password.html")
