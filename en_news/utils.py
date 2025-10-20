from .models import ExternalArticle, Source

def fetch_external_news(country='us', page_size=20, category=None, q=None):
    if not API_KEY:
        print("❌ NEWS_API_KEY not set in settings or environment.")
        return 0

    params = {"apiKey": API_KEY, "pageSize": page_size, "country": country}
    if category: params["category"] = category
    if q: params["q"] = q

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
        if not url or ExternalArticle.objects.filter(url=url).exists():
            continue

        title = item.get("title") or "No title"
        description = item.get("description") or item.get("content") or ""
        image_url = item.get("urlToImage")  # فقط لینک
        source_info = item.get("source", {})
        published_at = None

        if item.get("publishedAt"):
            try:
                dt = datetime.fromisoformat(item["publishedAt"].replace("Z", "+00:00"))
                published_at = timezone.make_aware(dt)
            except Exception:
                pass

        source_obj = None
        src_name = source_info.get("name")
        src_url = source_info.get("url")
        if src_name:
            source_obj, _ = Source.objects.get_or_create(
                name=src_name, defaults={"url": src_url}
            )

        article = ExternalArticle(
            source=source_obj,
            title=title,
            description=description,
            url=url,
            published_at=published_at,
            image_url=image_url,  # ذخیره لینک
        )

        try:
            article.save()
            saved += 1
            print(f"✅ ذخیره شد: {title[:50]}...")
        except Exception as e:
            print(f"⚠️ خطا در ذخیره ({url}): {e}")

    print(f"✅ Saved {saved} new external articles.")
    return saved
