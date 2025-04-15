from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Quiz, Question, QuizAttempt
from django.utils import timezone
from quiz_app.forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm

def home_view(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quizzes/home.html', {'quizzes': quizzes})

def home(request):
    return home_view(request)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quizzes/admin_dashboard.html', {'quizzes': quizzes})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            if user.is_superuser:
                return redirect('quizzes:admin_dashboard')
            else:
                return redirect('quizzes:home')
    else:
        form = RegisterForm()
    return render(request, 'quizzes/registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('quizzes:admin_dashboard')
            else:
                return redirect('quizzes:home')
        else:
            return render(request, 'quizzes/registration/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'quizzes/registration/login.html')

@login_required
def post_login_redirect(request):
    if request.user.is_superuser:
        return redirect('quizzes:admin_dashboard')
    else:
        return redirect('quizzes:home')

def user_logout(request):
    logout(request)
    return redirect('quizzes:login')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_quiz(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        topic = request.POST.get('topic')
        if Quiz.objects.filter(title=title).exists():
            messages.error(request, "A quiz with this title already exists.")
            return redirect('quizzes:add_quiz')
        if not title or not topic:
            messages.error(request, "Please fill in all required fields.")
            return redirect('quizzes:add_quiz')

        quiz = Quiz.objects.create(title=title, topic=topic)

        index = 1
        while f'question_{index}' in request.POST:
            q_text = request.POST.get(f'question_{index}')
            a = request.POST.get(f'option_a_{index}')
            b = request.POST.get(f'option_b_{index}')
            c = request.POST.get(f'option_c_{index}')
            d = request.POST.get(f'option_d_{index}')
            correct = request.POST.get(f'correct_{index}')
            if not all([q_text, a, b, c, d, correct]):
                messages.error(request, "All question fields must be filled.")
                quiz.delete()
                return redirect('quizzes:add_quiz')

            Question.objects.create(
                quiz=quiz,
                question_text=q_text,
                option_a=a,
                option_b=b,
                option_c=c,
                option_d=d,
                correct_answer=correct
            )
            index += 1

        messages.success(request, f"Quiz '{quiz.title}' has been created successfully with {index - 1} questions.")
        return redirect('quizzes:admin_dashboard')

    return render(request, 'quizzes/add_quiz.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_quiz(request, quiz_id=None):
    if quiz_id:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all()

        if request.method == 'POST':
            new_title = request.POST.get('title')
            new_topic = request.POST.get('topic')

            if new_title != quiz.title and Quiz.objects.filter(title=new_title).exists():
                messages.error(request, "A quiz with this title already exists.")
                return redirect('quizzes:edit_quiz', quiz_id=quiz.id)

            quiz.title = new_title
            quiz.topic = new_topic
            quiz.save()

            for i, question in enumerate(questions, start=1):
                question.question_text = request.POST.get(f'question_{i}')
                question.option_a = request.POST.get(f'option_a_{i}')
                question.option_b = request.POST.get(f'option_b_{i}')
                question.option_c = request.POST.get(f'option_c_{i}')
                question.option_d = request.POST.get(f'option_d_{i}')
                question.correct_answer = request.POST.get(f'correct_{i}')
                question.save()

            messages.success(request, f"Quiz '{quiz.title}' has been updated successfully.")
            return redirect('quizzes:admin_dashboard')

        return render(request, 'quizzes/edit_quiz.html', {'quiz': quiz, 'questions': questions})
    else:
        quizzes = Quiz.objects.all()
        return render(request, 'quizzes/edit_quiz_list.html', {'quizzes': quizzes})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        quiz_title = quiz.title
        quiz.delete()
        messages.success(request, f"Quiz '{quiz_title}' has been deleted successfully.")
        return redirect('quizzes:admin_dashboard')

    return render(request, 'quizzes/delete_quiz_confirm.html', {'quiz': quiz})

@login_required
def profile_view(request):
    attempts = QuizAttempt.objects.filter(user=request.user).order_by('-date_taken')
    return render(request, 'quizzes/profile.html', {'scores': attempts})

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    if request.method == 'POST':
        score = 0
        total = questions.count()
        
        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}')
            if user_answer == question.correct_answer:
                score += 1
        
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            date_taken=timezone.now()
        )
        
        messages.success(request, f"Quiz completed! Your score: {score}/{total}")
        return redirect('quizzes:user_scores')
    
    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })

@login_required
def user_scores(request):
    if request.user.is_superuser:
        attempts = QuizAttempt.objects.all().order_by('-date_taken')
        return render(request, 'quizzes/admin_scores.html', {'attempts': attempts})
    else:
        attempts = QuizAttempt.objects.filter(user=request.user).order_by('-date_taken')
        return render(request, 'quizzes/user_scores.html', {'attempts': attempts})

@login_required
def submit_quiz(request, quiz_id):
    return redirect('quizzes:take_quiz', quiz_id=quiz_id)

def base_view(request):
    return render(request, 'quizzes/base.html')
