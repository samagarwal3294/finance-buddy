"""Assemble the fetched data into an HTML email body."""
from datetime import datetime
from zoneinfo import ZoneInfo


def _arrow(pct):
    if pct is None:
        return "&mdash;", "#888"
    if pct > 0:
        return f"&#9650; {pct:+.2f}%", "#1a8f4c"   # green up
    if pct < 0:
        return f"&#9660; {pct:+.2f}%", "#c0392b"   # red down
    return f"{pct:+.2f}%", "#888"


def _num(x, dp=2):
    return f"{x:,.{dp}f}" if x is not None else "&mdash;"


def _market_section(market):
    html = ["<h2 style='color:#222;border-bottom:2px solid #eee;padding-bottom:4px'>Markets</h2>"]
    for group, rows in market.items():
        html.append(f"<h3 style='color:#444;margin:14px 0 6px'>{group}</h3>")
        html.append("<table style='width:100%;border-collapse:collapse;font-size:14px'>")
        for r in rows:
            label, color = _arrow(r["pct"])
            html.append(
                f"<tr>"
                f"<td style='padding:4px 8px;color:#333'>{r['name']}</td>"
                f"<td style='padding:4px 8px;text-align:right;color:#333'>{_num(r['last'])}</td>"
                f"<td style='padding:4px 8px;text-align:right;color:{color};font-weight:600'>{label}</td>"
                f"</tr>"
            )
        html.append("</table>")
    return "\n".join(html)


def _funds_section(funds):
    html = ["<h2 style='color:#222;border-bottom:2px solid #eee;padding-bottom:4px'>My Mutual Funds</h2>"]
    html.append("<table style='width:100%;border-collapse:collapse;font-size:14px'>")
    html.append(
        "<tr style='color:#888;font-size:12px;text-transform:uppercase'>"
        "<td style='padding:4px 8px'>Fund</td>"
        "<td style='padding:4px 8px;text-align:right'>NAV</td>"
        "<td style='padding:4px 8px;text-align:right'>1-Day</td>"
        "<td style='padding:4px 8px;text-align:right'>Value</td></tr>"
    )
    for f in funds:
        label, color = _arrow(f["pct"])
        nav = _num(f["nav"], 4)
        value = f"&#8377;{_num(f['value'])}" if f.get("value") else "&mdash;"
        html.append(
            f"<tr>"
            f"<td style='padding:4px 8px;color:#333'>{f['label']}</td>"
            f"<td style='padding:4px 8px;text-align:right;color:#333'>{nav}</td>"
            f"<td style='padding:4px 8px;text-align:right;color:{color};font-weight:600'>{label}</td>"
            f"<td style='padding:4px 8px;text-align:right;color:#333'>{value}</td>"
            f"</tr>"
        )
    html.append("</table>")
    html.append("<p style='font-size:11px;color:#aaa;margin-top:4px'>NAVs are end-of-day, "
                "published by AMCs with a 1-day lag. 1-Day = change vs previous published NAV.</p>")
    return "\n".join(html)


def _news_section(news):
    html = ["<h2 style='color:#222;border-bottom:2px solid #eee;padding-bottom:4px'>News</h2>"]
    for topic, regions in news.items():
        html.append(f"<h3 style='color:#444;margin:14px 0 6px'>{topic}</h3>")
        for region, items in regions.items():
            if not items:
                continue
            html.append(f"<p style='margin:6px 0 2px;color:#888;font-size:12px;"
                        f"text-transform:uppercase'>{region}</p>")
            html.append("<ul style='margin:0 0 8px;padding-left:18px;font-size:14px'>")
            for it in items:
                html.append(
                    f"<li style='margin:3px 0'>"
                    f"<a href='{it['link']}' style='color:#2a5db0;text-decoration:none'>{it['title']}</a>"
                    f"</li>"
                )
            html.append("</ul>")
    return "\n".join(html)


def build_html(market, funds, news):
    now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%A, %d %B %Y")
    body = f"""
    <div style="max-width:640px;margin:0 auto;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#333">
      <div style="text-align:center;padding:12px 0">
        <h1 style="margin:0;font-size:22px;color:#111">Daily Market &amp; News Digest</h1>
        <p style="margin:4px 0;color:#888;font-size:13px">{now}</p>
      </div>
      {_market_section(market)}
      <div style="height:18px"></div>
      {_funds_section(funds)}
      <div style="height:18px"></div>
      {_news_section(news)}
      <p style="text-align:center;color:#bbb;font-size:11px;margin-top:24px">
        Auto-generated digest &middot; data from yfinance, mfapi.in, Google News RSS.
        Not investment advice.
      </p>
    </div>
    """
    return body


def build_subject():
    now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y")
    return f"📈 Daily Digest — {now}"
