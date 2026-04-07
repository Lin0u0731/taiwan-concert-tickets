import requests
from bs4 import BeautifulSoup
import json
import datetime
import xml.etree.ElementTree as ET

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# -------------------------
# 地區分類
# -------------------------
def get_region(text):
    text = (text or "").upper()

    if any(k in text for k in ['台北','新北','桃園','基隆','LEGACY','ZEPP','北流','小巨蛋']):
        return "北部"
    if any(k in text for k in ['台中','彰化','雲林']):
        return "中部"
    if any(k in text for k in ['高雄','台南','屏東','嘉義','高流','駁二']):
        return "南部"
    if any(k in text for k in ['台東','花蓮','宜蘭']):
        return "東部"

    return "全台/其他"


# -------------------------
# KKTIX（主來源）
# -------------------------
def fetch_kktix_json():
    print("抓 KKTIX JSON...")
    url = "https://kktix.com/events.json"
    results = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()

        for event in data.get("entry", []):
            results.append({
                "title": event.get("title", ""),
                "location": event.get("venue_name", ""),
                "ticket_date": event.get("start_time", ""),
                "link": event.get("url", ""),
                "region": get_region(event.get("title", "") + event.get("venue_name", "")),
                "source": "KKTIX"
            })

    except Exception as e:
        print("KKTIX JSON 失敗:", e)

    return results


def fetch_kktix_html():
    print("抓 KKTIX HTML fallback...")
    url = "https://kktix.com/events"
    results = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        for card in soup.select(".event-item"):
            title_el = card.select_one(".event-title")
            link_el = card.select_one("a")

            results.append({
                "title": title_el.text.strip() if title_el else "",
                "location": "",
                "ticket_date": "",
                "link": link_el["href"] if link_el else "",
                "region": "全台",
                "source": "KKTIX"
            })

    except Exception as e:
        print("KKTIX HTML 失敗:", e)

    return results


def fetch_kktix():
    data = fetch_kktix_json()

    if len(data) == 0:
        print("⚠️ JSON 無資料，啟動 fallback")
        data = fetch_kktix_html()

    return data


# -------------------------
# Blow（補充來源）
# -------------------------
def fetch_blow():
    print("抓 Blow 音樂...")
    url = "https://blow.streetvoice.com/feed/"
    results = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        root = ET.fromstring(resp.content)

        for item in root.findall('.//item'):
            title = item.findtext('title') or ""
            link = item.findtext('link') or ""

            if any(k in title for k in ['專場','音樂祭','演唱會','巡演','開賣']):

                results.append({
                    "title": title,
                    "location": "詳見連結",
                    "ticket_date": "",
                    "link": link,
                    "region": get_region(title),
                    "source": "Blow"
                })

    except Exception as e:
        print("Blow 失敗:", e)

    return results


# -------------------------
# 文化部
# -------------------------
def fetch_culture():
    print("抓文化部...")
    url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=5"
    results = []

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()

        for item in data[:40]:
            show = item.get("showInfo", [{}])[0]

            results.append({
                "title": item.get("title", ""),
                "location": show.get("locationName", ""),
                "ticket_date": show.get("time", ""),
                "link": item.get("sourceWebPromote", ""),
                "region": get_region(item.get("title", "") + show.get("locationName", "")),
                "source": "文化部"
            })

    except Exception as e:
        print("文化部 失敗:", e)

    return results


# -------------------------
# 主流程
# -------------------------
def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    all_data = []

    # ⭐ 主資料
    all_data.extend(fetch_kktix())

    # ⭐ 補充資料
    all_data.extend(fetch_blow())
    all_data.extend(fetch_culture())

    # -------------------------
    # 去重
    # -------------------------
    seen = set()
    unique = []

    for d in all_data:
        key = d["title"] + d["link"]

        if key not in seen:
            d["last_updated"] = now
            unique.append(d)
            seen.add(key)

    # -------------------------
    # 輸出
    # -------------------------
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=4)

    print(f"完成 ✅ 共 {len(unique)} 筆資料")


if __name__ == "__main__":
    main()
print("KKTIX 筆數：", len([d for d in unique if d["source"] == "KKTIX"]))
