import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from xml.sax.saxutils import escape

FEED_URL = "https://wwepulsetoday.blogspot.com/feeds/posts/default?alt=rss"
PUBLICATION_NAME = "WWE Pulse Today"
LANGUAGE = "en"

with urllib.request.urlopen(FEED_URL) as response:
    data = response.read()

root = ET.fromstring(data)

now = datetime.now(timezone.utc)
cutoff = now - timedelta(days=2)

articles = []

for item in root.findall("./channel/item"):
    title = item.findtext("title")
    link = item.findtext("link")
    pub_date = item.findtext("pubDate")

    if not title or not link or not pub_date:
        continue

    published = parsedate_to_datetime(pub_date)

    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)

    published = published.astimezone(timezone.utc)

    if published >= cutoff:
        articles.append({
            "title": title,
            "link": link,
            "date": published.isoformat().replace("+00:00", "Z")
        })

xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset
    xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
'''

for article in articles:
    xml += f'''
  <url>
    <loc>{escape(article["link"])}</loc>
    <news:news>
      <news:publication>
        <news:name>{PUBLICATION_NAME}</news:name>
        <news:language>{LANGUAGE}</news:language>
      </news:publication>
      <news:publication_date>{article["date"]}</news:publication_date>
      <news:title>{escape(article["title"])}</news:title>
    </news:news>
  </url>
'''

xml += "\n</urlset>\n"

with open("news-sitemap.xml", "w", encoding="utf-8") as f:
    f.write(xml)

print(f"Generated sitemap with {len(articles)} recent articles.")
