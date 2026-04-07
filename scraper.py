import requests
from bs4 import BeautifulSoup
import json
import datetime
import cloudscraper

# --- 地區判斷邏輯 ---
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

# --- 第一道大門分支 A：KKTIX (因為鎖 GitHub IP，暫時關閉) ---
def fetch_kktix():
    print("暫時跳過 KKTIX，因機房 IP 被阻擋...")
    return []

# --- 第一道大門分支 B：iNDIEVOX ---
def fetch_indievox():
    print("正在從 iNDIEVOX 抓取資料...")
    url = "https://www.indievox.com/activity/list"
    scraper = cloudscraper.create_scraper()
    results = []
    try:
        resp = scraper.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        events = soup.find_all('div', class_='col-md-4')
        for event in events:
            try:
                title_tag = event.find('h5')
                if title_tag:
                    title = title_tag.text.strip()
                    a_tag = title_tag.find('a')
                    link = "https://www.indievox.com" + a_tag['href'] if a_tag and a_tag.has_attr('href') else url
                    results.append({
                        "title": title,
                        "location": "詳情見售票網", 
                        "ticket_date": "請見網頁",
                        "link": link,
                        "region": get_region(title),
                        "source": "iNDIEVOX"
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"iNDIEVOX 抓取失敗: {e}")
    return results

# --- 第三道大門：PTT 獨立音樂板 (完全無阻擋！) ---
def fetch_ptt():
    print("正在從 PTT 獨立音樂板抓取資料...")
    url = "https://www.ptt.cc/bbs/Indie-Music/index.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    try:
        # PTT 完全不擋，用最簡單的 requests 即可
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 抓取文章列表
        for div in soup.find_all("div", class_="r-ent"):
            title_elem = div.find("div", class_="title").a
            if title_elem:
                title = title_elem.text.strip()
                # 篩選標題包含特定關鍵字的文章
                if any(k in title for k in ['情報', '專場', '巡迴', '售票']):
                    link = "https://www.ptt.cc" + title_elem["href"]
                    results.append({
                        "title": title,
                        "location": "詳見 PTT 內文",
                        "ticket_date": "請見內文",
                        "link": link,
                        "region": get_region(title),
                        "source": "PTT Indie-Music"
                    })
    except Exception as e:
        print(f"PTT 抓取失敗: {e}")
    return results

# --- 主程式 ---
if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    all_data = []
    all_data.extend(fetch_kktix())
    all_data.extend(fetch_indievox())
    all_data.extend(fetch_ptt()) # 🌟 加入 PTT 資料！
    
    for e in all_data:
        e["last_updated"] = now
        
    if all_data:
        seen = set()
        unique_data = []
        for d in all_data:
            if d['link'] not in seen:
                unique_data.append(d)
                seen.add(d['link'])
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(unique_data, f, ensure_ascii=False, indent=4)
        print(f"任務完成！共整理出 {len(unique_data)} 筆全台演出資訊。")
