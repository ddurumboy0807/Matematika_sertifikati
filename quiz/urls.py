from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('levels/', views.level_select, name='level_select'),
    path('start/<int:level_num>/', views.start_quiz, name='start_quiz'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('answer/', views.answer_question, name='answer_question'),
    path('result/', views.result_view, name='result'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
