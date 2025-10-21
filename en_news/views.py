from django.shortcuts import render
from .models import ENArticle

def en_news_list(request):
    articles = ENArticle.objects.all().order_by('-published_at')[:40]
    return render(request, 'en_news/en_news_list.html', {'articles': articles})
