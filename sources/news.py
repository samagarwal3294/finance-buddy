"""Fetch headlines per topic (India + Global) from RSS feeds."""
import json
import os
import feedparser

CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "feeds.json")
MAX_PER_FEED = 4


def _headlines(url):
    try:
        parsed = feedparser.parse(url)
        items = []
        for entry in parsed.entries[:MAX_PER_FEED]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            # Google News titles often end with ' - Source'; keep as-is, it's useful
            if title:
                items.append({"title": title, "link": link})
        return items
    except Exception as e:
        print(f"[news] feed failed {url}: {e}")
        return []


def fetch_news():
    with open(CONFIG) as f:
        feeds = json.load(f)

    result = {}
    for topic, regions in feeds.items():
        result[topic] = {region: _headlines(url) for region, url in regions.items()}
    return result


if __name__ == "__main__":
    from pprint import pprint
    pprint(fetch_news())
