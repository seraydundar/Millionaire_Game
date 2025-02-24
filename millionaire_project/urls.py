from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from quiz.views import (
    intro_view,
    home_view,
    start_game_view,
    random_question_view,
    continue_game_view,   # Bu satırı ekleyin
    withdraw_view,        # Bu satırı ekleyin
    custom_logout,
    register_view,
    add_question_view,
)

urlpatterns = [
    path('', intro_view, name='intro'),
    path('home/', home_view, name='home'),
    path('start-game/', start_game_view, name='start_game'),
    path('random-question/<int:level>/', random_question_view, name='random_question'),
    path('continue-game/<int:next_level>/', continue_game_view, name='continue_game'),  # Ekleyin
    path('withdraw/', withdraw_view, name='withdraw'),  # Ekleyin
    path('login/', auth_views.LoginView.as_view(template_name="quiz/login.html"), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', register_view, name='register'),
    path('add-question/', add_question_view, name='add_question'),
    path('admin/', admin.site.urls),
]
