from django.shortcuts import render
from .models import NewsArticle
from .services import fetch_news_from_isna

def news_list(request):
    if request.GET.get('refresh') == '1':
        saved = fetch_news_from_isna(limit=20)
        print(f"Saved {saved} new articles.")

    articles = NewsArticle.objects.all().order_by('-published_at')[:40]
    return render(request, 'news/news_list.html', {'articles': articles})
