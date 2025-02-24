# quiz/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Question

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="İsim")
    last_name = forms.CharField(max_length=30, required=True, label="Soyisim")
    email = forms.EmailField(required=True, label="E-posta")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")




class AddQuestionForm(forms.Form):
    question_text = forms.CharField(widget=forms.Textarea, label="Soru Metni")
    level = forms.ChoiceField(choices=[(i, f"Seviye {i}") for i in range(1, 13)], label="Seviye")
    price = forms.IntegerField(label="Ödül")
    correct_answer = forms.CharField(max_length=255, label="Doğru Cevap")
    incorrect_answer1 = forms.CharField(max_length=255, label="Yanlış Cevap 1")
    incorrect_answer2 = forms.CharField(max_length=255, label="Yanlış Cevap 2")
    incorrect_answer3 = forms.CharField(max_length=255, label="Yanlış Cevap 3")