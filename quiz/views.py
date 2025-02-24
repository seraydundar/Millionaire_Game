import random

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Question, CorrectAnswer, IncorrectAnswer
from .forms import RegisterForm, AddQuestionForm


def intro_view(request):
    """
    Lotus Oyunları Kim Milyoner Olmak İster adlı giriş (intro) sayfasını 5 saniye gösterir,
    sonra otomatik olarak /home sayfasına yönlendirir.
    """
    return render(request, "quiz/intro.html")


from .models import Profile

def home_view(request):
    current_game_prize = request.session.get('current_game_prize', 0)
    total_prize = 0
    # Tüm kullanıcılar için sıralama (Profile nesneleri varsa)
    top_total = Profile.objects.order_by('-balance')[:10]
    top_single = Profile.objects.order_by('-max_game_prize')[:10]
    
    if request.user.is_authenticated:
        profile = request.user.profile
        profile.refresh_from_db()  # Güncel verileri alır
        total_prize = profile.balance
    
    return render(request, "quiz/home.html", {
        "current_prize": current_game_prize,
        "total_prize": total_prize,
        "top_total": top_total,
        "top_single": top_single,
    })







@login_required
def start_game_view(request):
    request.session['current_game_prize'] = 0
    return redirect('random_question', level=1)




@login_required
def random_question_view(request, level=1):
    """
    Belirli seviyedeki rastgele bir soruyu gösterir.
    POST geldiğinde formdan gelen question_id'ye göre aynı soruyu tekrar bulur,
    doğru/yanlış kontrolü yapar.
    
    İstenen mantık:
      - Doğru cevap verildiğinde current_game_prize, o sorunun ödülü (question.price) olarak ayarlanır.
      - Yanlış cevap verildiğinde, kullanıcının o ana kadar elde ettiği current_game_prize ödül olarak alınır.
      - Seviye 6'dan itibaren süre (timer) gösterilmez.
      - Doğru cevap sonrası, seviye 1-2 için direkt sonraki soruya, seviye 3 ve üstü için "Devam Et / Çekil" karar sayfasına yönlendirme yapılır.
    """
    questions = Question.objects.filter(level=level)
    if not questions.exists():
        return render(request, "quiz/random_question.html", {
            "error": "Bu seviyede soru bulunamadı.",
            "level": level
        })

    # Referans için ödül değerlerini içeren levels listesi (görsel amaçlı)
    levels = [
        {'level': 1, 'reward': 100},
        {'level': 2, 'reward': 500},
        {'level': 3, 'reward': 1000},
        {'level': 4, 'reward': 2000},
        {'level': 5, 'reward': 5000},
        {'level': 6, 'reward': 10000},
        {'level': 7, 'reward': 20000},
        {'level': 8, 'reward': 50000},
        {'level': 9, 'reward': 100000},
        {'level': 10, 'reward': 200000},
        {'level': 11, 'reward': 500000},
        {'level': 12, 'reward': 1000000},
    ]

    if request.method == "POST":
        # Formdan gelen soru ID'sini al
        question_id = request.POST.get('question_id')
        try:
            question_id = int(question_id)
            question = Question.objects.get(id=question_id)
        except (ValueError, TypeError, Question.DoesNotExist):
            messages.error(request, "Bir hata oluştu, lütfen tekrar deneyin.")
            return redirect("home")

        answers = list(question.incorrect_answers.all())
        answers.append(question.correct_answer)

        selected_answer_id = request.POST.get("selected_answer")
        try:
            selected_answer_id = int(selected_answer_id)
        except (ValueError, TypeError):
            selected_answer_id = None

        # current_game_prize: o ana kadar kazanılan ödül (her sorunun ödülü ayrı)
        current_game_prize = request.session.get('current_game_prize', 0)

        if selected_answer_id == question.correct_answer.id:
            messages.success(request, "Tebrikler, doğru cevap!")
            # Sadece bu sorunun ödülünü alır (toplam eklemez)
            current_game_prize = question.price  
            request.session['current_game_prize'] = current_game_prize

            # Profilin güncel değerini alıp max_game_prize'yi güncelleyelim:
            user_profile = request.user.profile
            if current_game_prize > user_profile.max_game_prize:
                user_profile.max_game_prize = current_game_prize
                user_profile.save()

            next_level = level + 1
            if next_level > 12:
                user_profile = request.user.profile
                user_profile.balance += current_game_prize
                user_profile.save()
                # Oyun tamamlandığında isteğe bağlı sıfırlayabilirsiniz.
                request.session['current_game_prize'] = 0
                return render(request, "quiz/game_completed.html", {
                    "message": "Tüm seviyeleri başarıyla bitirdiniz!"
                })
            else:
                if level < 3:
                    return redirect("random_question", level=next_level)
                else:
                    context = {
                        "next_level": next_level,
                        "current_game_prize": current_game_prize,
                        "levels": levels,
                        "current_level": level,
                    }
                    return render(request, "quiz/decision.html", context)
        else:
            messages.error(request, "Yanlış cevap! Elendiniz.")
            user_profile = request.user.profile
            # Yanlış cevap verildiğinde, ödül olarak o ana kadar kazanılan current_game_prize kullanılsın.
            final_reward = request.session.get('current_game_prize', 0)
            user_profile.balance += final_reward
            user_profile.save()
            # NOT: Bu sefer current_game_prize sıfırlamıyoruz, böylece home_view güncel değeri gösterebilsin.
            return redirect("home")
    else:
        # GET: Rastgele bir soru seç
        question = random.choice(questions)
        answers = list(question.incorrect_answers.all())
        answers.append(question.correct_answer)
        random.shuffle(answers)
        request.session.setdefault('current_game_prize', 0)

    context = {
        "question": question,
        "answers": answers,
        "level": level,
        "current_level": level,
        "levels": levels,
    }
    return render(request, "quiz/random_question.html", context)




@login_required
def continue_game_view(request, next_level):
    """
    Kullanıcı "Devam Et" seçeneğini seçtiğinde, bir sonraki seviyeye yönlendirilir.
    """
    return redirect("random_question", level=next_level)


@login_required
def withdraw_view(request):
    """
    Kullanıcı "Çekil" seçeneğini seçerse, mevcut güncel kazanç profilindeki toplam kazanca eklenir
    ve oyuncu ana sayfaya yönlendirilir. (current_game_prize sıfırlanmaz.)
    """
    current_game_prize = request.session.get('current_game_prize', 0)
    user_profile = request.user.profile
    user_profile.balance += current_game_prize
    user_profile.save()
    messages.info(request, f"Oyundan çekildiniz. Toplam kazancınız: {user_profile.balance} TL")
    return redirect("home")



def custom_logout(request):
    """
    Kullanıcının oturumunu sonlandırır ve ana sayfaya yönlendirir.
    """
    logout(request)
    return redirect('home')


def register_view(request):
    """
    Kullanıcı kayıt işlemini gerçekleştirir.
    Kayıt sonrası otomatik giriş yapar ve ana sayfaya yönlendirir.
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Kayıt başarılı!")
            return redirect("home")
        else:
            messages.error(request, "Kayıt başarısız. Lütfen bilgilerinizi kontrol ediniz.")
    else:
        form = RegisterForm()
    return render(request, "quiz/register.html", {"form": form})


@login_required
def add_question_view(request):
    """
    Giriş yapmış kullanıcıların yeni soru eklemelerine olanak tanır.
    Form verileriyle Question, CorrectAnswer ve IncorrectAnswer oluşturulur.
    """
    if request.method == "POST":
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            question_text = form.cleaned_data["question_text"]
            level = form.cleaned_data["level"]
            price = form.cleaned_data["price"]
            correct_answer_text = form.cleaned_data["correct_answer"]
            inc1 = form.cleaned_data["incorrect_answer1"]
            inc2 = form.cleaned_data["incorrect_answer2"]
            inc3 = form.cleaned_data["incorrect_answer3"]

            q = Question.objects.create(
                question_text=question_text,
                level=level,
                price=price
            )
            CorrectAnswer.objects.create(question=q, answer_text=correct_answer_text)
            IncorrectAnswer.objects.create(question=q, answer_text=inc1)
            IncorrectAnswer.objects.create(question=q, answer_text=inc2)
            IncorrectAnswer.objects.create(question=q, answer_text=inc3)

            messages.success(request, "Yeni soru başarıyla eklendi!")
            return redirect("home")
    else:
        form = AddQuestionForm()

    return render(request, "quiz/add_question.html", {"form": form})
