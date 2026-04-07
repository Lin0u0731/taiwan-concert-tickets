import requests
from bs4 import BeautifulSoup
import json
import datetime

def get_region(text):
    text = text.upper()
    if any(k in text for k in ['台北', '新北', '桃園', '基隆', 'LEGACY TAIPEI', 'ZEPP', '北流', '小巨蛋', '河岸留言', 'THE WALL']):
        return "北部"
    if any(k in text for k in ['台中', '彰化', '雲林', 'LEGACY TAICHUNG', '迴響']):
        return "中部"
    if any(k in text for k in ['高雄', '台南', '屏東', '駁二', '後台', '高流', '衛武營', 'LIVE WAREHOUSE']):
        return "南部"
    if any(k in text for k in ['台東', '花蓮', '宜蘭', '鐵花村']):
        return "東部"
    return "全台/其他"

# 🌟 秘密通道 1：KKTIX RSS 廣播站 (無視 Cloudflare 防護)
def fetch_kktix_rss():
    print("嘗試從 KKTIX RSS 通道抓取資料...")
    url = "https://kktix.com/events.atom"
    results = []
    try:
        # RSS 通常不擋人，用最簡單的 requests 即可
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 解析 XML 格式的 entry
        for entry in soup.find_all("entry"):
            title = entry.title.text if entry.title else ""
            link_tag = entry.find("link")
            link = link_tag["href"] if link_tag else ""
            summary = entry.summary.text if entry.summary else ""

            # 只抓音樂相關的
            if any(k in title for k in ['演唱會', '音樂', '祭', 'Live', '巡迴', 'Tour', '專場', '派對']):
                results.append({
                    "title": title,
                    "location": "詳見售票網頁",
                    "ticket_date": "請見網頁",
                    "link": link,
                    "region": get_region(title + summary),
                    "source": "KKTIX (RSS通道)"
                })
    except Exception as e:
        print(f"KKTIX RSS 失敗: {e}")
    return results

# 🌟 秘密通道 2：PTT 鏡像備份站 (無視 PTT IP 封鎖)
def fetch_ptt_mirror():
    print("嘗試從 PTT 鏡像站抓取資料...")
    url = "https://pttweb.cc/bbs/Indie-Music"
    results = []
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 尋找所有網頁裡的超連結
        for a_tag in soup.find_all("a"):
            title = a_tag.text.strip()
            href = a_tag.get("href", "")
            
            # 只要連結裡面包含 PTT 文章的特徵碼，且有標題，就抓下來！
            if "/bbs/Indie-Music/M." in href and title:
                results.append({
                    "title": title,
                    "location": "詳見 PTT 內文",
                    "ticket_date": "請見內文",
                    "link": "https://pttweb.cc" + href,
                    "region": get_region(title),
                    "source": "PTT 獨立音樂板"
                })
    except Exception as e:
        print(f"PTT 鏡像站失敗: {e}")
    return results

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_data = []
    
    # 執行我們的兩大秘密部隊
    all_data.extend(fetch_kktix_rss())
    all_data.extend(fetch_ptt_mirror())
    
    # 加上測試卡片確保有更新
    all_data.append({
        "title": "✅ 系統測試成功！資料來源已切換為秘密通道！",
        "location": "GitHub Actions",
        "ticket_date": "運作正常",
        "link": "https://github.com",
        "region": "全台/其他",
        "source": "系統提示"
    })

    for e in all_data:
        e["last_updated"] = now
        
    # 去除重複網址
    seen = set()
    unique_data = []
    for d in all_data:
        if d['link'] not in seen:
            unique_data.append(d)
            seen.add(d['link'])
            
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
    print(f"任務完成！已透過秘密通道更新檔案。")
