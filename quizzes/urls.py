from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.base_view, name='base'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('user-scores/', views.user_scores, name='user_scores'),
    path('add-quiz/', views.add_quiz, name='add_quiz'),
    path('edit-quiz/', views.edit_quiz, name='edit_quiz'),
    path('delete-quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('edit-quiz/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('take-quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('submit-quiz/<int:quiz_id>/', views.submit_quiz, name='submit_quiz'),
]