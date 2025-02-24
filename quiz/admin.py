from django.contrib import admin
from .models import Question, CorrectAnswer, IncorrectAnswer

admin.site.register(Question)
admin.site.register(CorrectAnswer)
admin.site.register(IncorrectAnswer)
