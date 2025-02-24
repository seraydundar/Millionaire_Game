from .models import Profile

def scoreboard_context(request):
    top_total = Profile.objects.order_by('-balance')[:10]
    top_single = Profile.objects.order_by('-max_game_prize')[:10]
    return {
        'top_total': top_total,
        'top_single': top_single,
    }