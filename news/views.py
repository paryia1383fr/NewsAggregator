from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Article
import feedparser
from datetime import datetime
from django.core.files.base import ContentFile
import requests
import re
from django.utils import timezone

def fetch_news():
    feed = feedparser.parse("https://www.isna.ir/rss")
    for entry in feed.entries:
        title = entry.title
        description = entry.get("summary", "")
        url = entry.link
        published = entry.get("published_parsed")
        published_at = timezone.make_aware(datetime(*published[:6])) if published else None

        # جلوگیری از اخبار تکراری
        if Article.objects.filter(url=url).exists():
            continue

        article = Article(
            title=title,
            description=description,
            url=url,
            published_at=published_at
        )

        # گرفتن تصویر
        image_url = None
        if "enclosures" in entry and entry.enclosures:
            image_url = entry.enclosures[0].get("href")
        else:
            match = re.search(r'<img.*?src="(.*?)"', description)
            if match:
                image_url = match.group(1)

       # قبل از ذخیره مقاله
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    file_name = image_url.split("/")[-1]
                    if not file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                        file_name += ".jpg"
                    article.image_url.save(file_name, ContentFile(response.content), save=False)
            except Exception as e:
                print("❌ خطا در دانلود عکس:", e)

        article.save()

def news_list(request):
    fetch_news()
    articles = Article.objects.all().order_by('-published_at')[:15]
    return render(request, 'news/new_list.html', {'articles': articles})
