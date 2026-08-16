"""Daily market + funds + news digest -> email.

Run locally:   python main.py            (sends email if env vars set)
               python main.py --dry-run  (writes preview.html, no email)
"""
import sys

from sources.market import fetch_market
from sources.funds import fetch_funds
from sources.news import fetch_news
from digest import build_html, build_subject


def main():
    dry = "--dry-run" in sys.argv

    print("Fetching markets...")
    market = fetch_market()
    print("Fetching funds...")
    funds = fetch_funds()
    print("Fetching news...")
    news = fetch_news()

    html = build_html(market, funds, news)
    subject = build_subject()

    if dry:
        with open("preview.html", "w") as f:
            f.write(html)
        print("Wrote preview.html")
        return

    from mailer import send_email
    send_email(subject, html)


if __name__ == "__main__":
    main()
