from django.urls import path
from .api_views import get_random_question

urlpatterns = [
    path('question/<int:level>/', get_random_question, name='api_random_question'),
]
