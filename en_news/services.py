import requests
from django.utils import timezone
from datetime import datetime
from .models import ENArticle, ENSource
from django.conf import settings

def fetch_en_news():
    api_key = getattr(settings, "NEWS_API_KEY", None)
    if not api_key:
        raise ValueError("NEWS_API_KEY is missing in settings")

    url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()

    if data.get("status") != "ok":
        print("Error fetching news:", data)
        return

    for item in data.get("articles", []):
        article_url = item.get("url")
        if not article_url or ENArticle.objects.filter(url=article_url).exists():
            continue

        title = item.get("title") or "No title"
        description = item.get("description") or ""
        image_url = item.get("urlToImage")
        published_at = None

        if item.get("publishedAt"):
            try:
                dt = datetime.fromisoformat(item["publishedAt"].replace("Z", "+00:00"))
                published_at = timezone.make_aware(dt)
            except Exception:
                pass

        source_data = item.get("source", {})
        source_name = source_data.get("name")
        source_url = source_data.get("url")
        source_obj = None

        if source_name:
            source_obj, _ = ENSource.objects.get_or_create(
                name=source_name,
                defaults={"url": source_url},
            )

        ENArticle.objects.create(
            source=source_obj,
            title=title,
            description=description,
            url=article_url,
            published_at=published_at,
            image_url=image_url,
        )

    print("✅ English news fetched successfully.")
