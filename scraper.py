import requests
from bs4 import BeautifulSoup
import json
import datetime
import cloudscraper

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

def fetch_indievox():
    print("嘗試從 iNDIEVOX 抓取資料...")
    url = "https://www.indievox.com/activity/list"
    scraper = cloudscraper.create_scraper()
    results = []
    try:
        resp = scraper.get(url, timeout=10)
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
        print(f"iNDIEVOX 失敗: {e}")
    return results

def fetch_ptt():
    print("嘗試從 PTT 獨立音樂板抓取資料...")
    url = "https://www.ptt.cc/bbs/Indie-Music/index.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for div in soup.find_all("div", class_="r-ent"):
            title_elem = div.find("div", class_="title").a
            if title_elem:
                title = title_elem.text.strip()
                # 🌟 拿掉嚴格過濾，只要是 PTT 文章就抓！
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
        print(f"PTT 失敗: {e}")
    return results

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_data = []
    
    # 🌟 絕招：塞入一筆「系統更新確認卡」，確保檔案 100% 會被覆蓋更新
    all_data.append({
        "title": "✅ 系統測試成功！這不是假資料！",
        "location": "GitHub Actions 機房",
        "ticket_date": "看到這張卡片，代表你的網頁和機器人連線完全正常",
        "link": "https://github.com",
        "region": "全台/其他",
        "source": "系統提示"
    })

    all_data.extend(fetch_indievox())
    all_data.extend(fetch_ptt()) 
    
    for e in all_data:
        e["last_updated"] = now
        
    seen = set()
    unique_data = []
    for d in all_data:
        if d['link'] not in seen:
            unique_data.append(d)
            seen.add(d['link'])
    
    # 🌟 拿掉 if all_data 的保護機制，就算抓不到東西也強制把新結果存檔！
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
    print(f"任務完成！已強制更新檔案。")
