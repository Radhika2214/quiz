from django import forms
from quizzes.models import Quiz, Question


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'topic']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']


from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']
