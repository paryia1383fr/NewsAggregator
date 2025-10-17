import requests
from datetime import datetime
from urllib.parse import urlparse
from django.utils import timezone
from django.core.files.base import ContentFile
from django.conf import settings
from .models import ExternalArticle, Source

NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
API_KEY = getattr(settings, "NEWS_API_KEY", None)

def fetch_external_news(country='us', page_size=20, category=None, q=None):
    if not API_KEY:
        print("❌ NEWS_API_KEY not set in settings or environment.")
        return 0

    params = {
        "apiKey": API_KEY,
        "pageSize": page_size,
        "country": country,
    }
    if category:
        params["category"] = category
    if q:
        params["q"] = q

    try:
        resp = requests.get(NEWS_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("❌ News API request failed:", e)
        return 0

    saved = 0

    for item in data.get("articles", []):
        url = item.get("url")
        if not url:
            continue

        # ⛔ بررسی اینکه آیا این مقاله قبلاً وجود دارد یا نه
        if ExternalArticle.objects.filter(url=url).exists():
            print(f"⚠️ خبر تکراری (skip): {url}")
            continue

        title = item.get("title") or "No title"
        description = item.get("description") or item.get("content") or ""
        image_url = item.get("urlToImage")
        source_info = item.get("source", {})
        published_at_raw = item.get("publishedAt")

        # 🕒 تاریخ انتشار
        published_at = None
        if published_at_raw:
            try:
                dt = datetime.fromisoformat(published_at_raw.replace("Z", "+00:00"))
                published_at = timezone.make_aware(dt)
            except Exception:
                published_at = None

        # 📰 منبع خبر
        source_obj = None
        src_name = source_info.get("name")
        src_url = source_info.get("url")
        if src_name:
            source_obj, _ = Source.objects.get_or_create(name=src_name, defaults={"url": src_url})

        # 📦 ایجاد آبجکت مقاله
        article = ExternalArticle(
            source=source_obj,
            title=title,
            description=description,
            url=url,
            published_at=published_at,
        )

        # 🖼 ذخیره عکس
        if image_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                img_resp = requests.get(image_url, timeout=10, headers=headers)
                if img_resp.status_code == 200 and img_resp.content:
                    parsed = urlparse(image_url)
                    file_name = parsed.path.split("/")[-1] or "image.jpg"
                    if not file_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                        file_name += ".jpg"
                    article.image.save(file_name, ContentFile(img_resp.content), save=False)
            except Exception as e:
                print("⚠️ خطا در دانلود عکس:", e)

        # 💾 ذخیره در دیتابیس
        try:
            article.save()
            saved += 1
            print(f"✅ ذخیره شد: {title[:50]}...")
        except Exception as e:
            print(f"⚠️ خطا در ذخیره ({url}): {e}")

    print(f"✅ Saved {saved} new external articles.")
    return saved
