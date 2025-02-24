from rest_framework import serializers
from .models import Question, CorrectAnswer, IncorrectAnswer

class CorrectAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectAnswer
        fields = ['id', 'answer_text']

class IncorrectAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncorrectAnswer
        fields = ['id', 'answer_text']

class QuestionSerializer(serializers.ModelSerializer):
    correct_answer = CorrectAnswerSerializer(read_only=True)
    incorrect_answers = IncorrectAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'level', 'price', 'correct_answer', 'incorrect_answers']
