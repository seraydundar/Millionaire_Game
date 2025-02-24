import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Question
from .serializers import QuestionSerializer

@api_view(['GET'])
def get_random_question(request, level):
    questions = Question.objects.filter(level=level)
    if not questions.exists():
        return Response({"error": "Bu seviyede soru bulunamadı."}, status=404)
    question = random.choice(questions)
    serializer = QuestionSerializer(question)
    return Response(serializer.data)
