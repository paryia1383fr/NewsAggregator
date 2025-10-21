import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .models import NewsArticle
import re

def fetch_news_from_isna(limit=20):
    RSS_URL = "https://www.isna.ir/rss"
    try:
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ خطا در دریافت RSS ایسنا: {e}")
        return 0

    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")[:limit]
    added_count = 0

    for item in items:
        title = item.title.text if item.title else "بدون عنوان"
        description = item.description.text if item.description else ""
        url = item.link.text if item.link else None
        pub_date = item.pubDate.text if item.pubDate else None
        
        # روش‌های مختلف برای استخراج تصویر
        image_url = None
        
        # روش ۱: از تگ enclosure
        enclosure = item.find("enclosure")
        if enclosure and enclosure.get('url'):
            image_url = enclosure.get('url')
            print(f"📸 روش ۱ - enclosure: {image_url}")
        
        # روش ۲: از تگ media:content
        if not image_url:
            media_content = item.find("media:content")
            if media_content and media_content.get('url'):
                image_url = media_content.get('url')
                print(f"📸 روش ۲ - media:content: {image_url}")
        
        # روش ۳: از description با regex
        if not image_url and description:
            # جستجو برای لینک تصویر در description
            img_patterns = [
                r'src="([^"]+\.(jpg|jpeg|png|gif))"',
                r'src="(https://[^"]+)"',
                r'<img[^>]+src="([^"]+)"'
            ]
            
            for pattern in img_patterns:
                match = re.search(pattern, description, re.IGNORECASE)
                if match:
                    image_url = match.group(1)
                    print(f"📸 روش ۳ - از description: {image_url}")
                    break
        
        # روش ۴: اگر هنوز تصویری پیدا نشد، از محتوای CDATA استخراج کنیم
        if not image_url:
            # بعضی RSS ها تصویر رو در CDATA قرار می‌دن
            cdata_match = re.search(r'<img[^>]*src="([^"]+)"[^>]*>', str(item), re.IGNORECASE)
            if cdata_match:
                image_url = cdata_match.group(1)
                print(f"📸 روش ۴ - از CDATA: {image_url}")

        # لاگ برای دیباگ
        print(f"✅ عنوان: {title[:50]}...")
        print(f"📸 تصویر یافت شده: {image_url}")
        print("---")

        if not url or NewsArticle.objects.filter(url=url).exists():
            continue

        published_at = None
        try:
            published_at = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            try:
                published_at = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            except Exception:
                pass

        NewsArticle.objects.create(
            title=title,
            description=description,
            url=url,
            image_url=image_url,
            published_at=published_at,
        )
        added_count += 1

    print(f"✅ {added_count} خبر از ایسنا اضافه شد.")
    return added_count