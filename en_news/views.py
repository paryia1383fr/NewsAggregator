from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from .models import ExternalArticle
from .utils import fetch_external_news

def external_news_list(request):
    # وقتی ?refresh=1 باشه از API میگیره و ذخیره میکنه
    if request.GET.get('refresh') == '1':
        saved = fetch_external_news(country='us', page_size=20)
        print(f"Saved {saved} new external articles.")
    articles = ExternalArticle.objects.all().order_by('-published_at')[:40]
    return render(request, 'external_news/external_list.html', {'articles': articles})
