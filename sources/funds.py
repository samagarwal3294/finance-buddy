"""Resolve scheme codes by name and fetch latest NAV + day change from mfapi.in.

mfapi.in endpoints (free, no key):
  - https://api.mfapi.in/mf/search?q=<name>   -> [{schemeCode, schemeName}, ...]
  - https://api.mfapi.in/mf/<code>            -> {meta, data:[{date, nav}, ...]}
"""
import json
import os
import requests

CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "funds.json")
SEARCH = "https://api.mfapi.in/mf/search"
DETAIL = "https://api.mfapi.in/mf/{code}"
TIMEOUT = 20


def _resolve_code(fund):
    """Find the scheme code matching the include/exclude keyword filters."""
    if fund.get("code"):
        return fund["code"]
    try:
        r = requests.get(SEARCH, params={"q": fund["search"]}, timeout=TIMEOUT)
        r.raise_for_status()
        candidates = r.json()
    except Exception as e:
        print(f"[funds] search failed for {fund['label']}: {e}")
        return None

    inc = [k.lower() for k in fund.get("must_include", [])]
    exc = [k.lower() for k in fund.get("must_exclude", [])]
    matches = []
    for c in candidates:
        name = c["schemeName"].lower()
        if all(k in name for k in inc) and not any(k in name for k in exc):
            matches.append(c)
    if not matches:
        print(f"[funds] no match for {fund['label']}")
        return None
    # shortest name is almost always the plain 'Regular - Growth' variant
    best = min(matches, key=lambda c: len(c["schemeName"]))
    return best["schemeCode"]


def _nav(code):
    """Return (scheme_name, latest_nav, nav_date, pct_change)."""
    try:
        r = requests.get(DETAIL.format(code=code), timeout=TIMEOUT)
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        print(f"[funds] detail failed for {code}: {e}")
        return None, None, None, None

    name = payload.get("meta", {}).get("scheme_name")
    data = payload.get("data", [])
    if not data:
        return name, None, None, None
    latest = float(data[0]["nav"])
    date = data[0]["date"]
    pct = None
    if len(data) > 1:
        prev = float(data[1]["nav"])
        pct = (latest - prev) / prev * 100 if prev else None
    return name, latest, date, pct


def fetch_funds():
    with open(CONFIG) as f:
        funds = json.load(f)

    rows = []
    for fund in funds:
        code = _resolve_code(fund)
        if not code:
            rows.append({"label": fund["label"], "nav": None, "pct": None,
                         "date": None, "value": None, "resolved": None})
            continue
        name, nav, date, pct = _nav(code)
        units = fund.get("units")
        value = round(nav * units, 2) if (nav and units) else None
        rows.append({
            "label": fund["label"], "resolved": name, "code": code,
            "nav": nav, "date": date, "pct": pct, "units": units, "value": value,
        })
    return rows


if __name__ == "__main__":
    from pprint import pprint
    pprint(fetch_funds())
