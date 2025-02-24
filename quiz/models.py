from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)
    max_game_prize = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.balance} TL"

class Question(models.Model):
    LEVEL_CHOICES = [(i, f"Seviye {i}") for i in range(1, 13)]

    question_text = models.TextField(verbose_name="Soru Metni")
    level = models.PositiveSmallIntegerField(
        choices=LEVEL_CHOICES,
        verbose_name="Seviye"
    )
    price = models.PositiveIntegerField(verbose_name="Ödül", default=0)

    def __str__(self):
        return f"{self.question_text} (Seviye: {self.level})"

class CorrectAnswer(models.Model):
    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name="correct_answer",
        verbose_name="İlgili Soru"
    )
    answer_text = models.CharField(max_length=255, verbose_name="Doğru Cevap")

    def __str__(self):
        return f"Doğru Cevap: {self.answer_text}"

class IncorrectAnswer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="incorrect_answers",
        verbose_name="İlgili Soru"
    )
    answer_text = models.CharField(max_length=255, verbose_name="Yanlış Cevap")

    def __str__(self):
        return f"Yanlış Cevap: {self.answer_text}"
