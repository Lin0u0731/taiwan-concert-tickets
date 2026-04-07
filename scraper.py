import requests
import json
import datetime

def get_region(text):
    text = text.upper()
    if any(k in text for k in ['台北', '新北', '桃園', '基隆', 'LEGACY TAIPEI', 'ZEPP', '北流', '小巨蛋', '河岸留言', 'THE WALL', 'NUZONE']):
        return "北部"
    if any(k in text for k in ['台中', '彰化', '雲林', 'LEGACY TAICHUNG', '迴響']):
        return "中部"
    if any(k in text for k in ['高雄', '台南', '屏東', '駁二', '後台', '高流', '衛武營', 'LIVE WAREHOUSE']):
        return "南部"
    if any(k in text for k in ['台東', '花蓮', '宜蘭', '鐵花村']):
        return "東部"
    return "全台/其他"

# 🌟 絕對不會被擋的政府開放資料！
def fetch_culture_api():
    print("正在從『文化部開放資料庫』抓取全台流行音樂展演資訊...")
    # category=5 代表「流行音樂」分類
    url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=5"
    results = []
    
    try:
        # 政府 API 對爬蟲非常友善，直接抓取即可
        resp = requests.get(url, timeout=15)
        data = resp.json()
        
        # 為了避免資料量太大網頁跑不動，我們抓取最新的 60 筆活動
        for item in data[:60]:
            title = item.get("title", "")
            
            # 取得展演資訊 (通常會有多個場次，我們取第一場當代表)
            show_info = item.get("showInfo", [])
            if not show_info:
                continue
                
            first_show = show_info[0]
            location = first_show.get("locationName", "未提供地點")
            time = first_show.get("time", "請見網頁公告")
            
            # 嘗試取得售票連結，如果沒有就給它空字串
            link = item.get("sourceWebPromote", "")
            if not link or not link.startswith("http"):
                link = "https://cloud.culture.tw/" # 如果沒網址，就導回文化部
                
            results.append({
                "title": title,
                "location": location,
                "ticket_date": f"演出時間：{time}", # 文化部 API 提供的是演出時間，我們拿來代替
                "link": link,
                "region": get_region(title + location),
                "source": "文化部 OpenData"
            })
            
    except Exception as e:
        print(f"文化部 API 抓取失敗: {e}")
        
    return results

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_data = []
    
    # 執行文化部 API 抓取
    all_data.extend(fetch_culture_api())
    
    # 測試卡片
    all_data.append({
        "title": "🎉 系統大升級：已成功介接文化部流行音樂資料庫！",
        "location": "全台灣",
        "ticket_date": "這是一個真實的開放資料來源，不再怕被擋了！",
        "link": "https://github.com",
        "region": "全台/其他",
        "source": "系統提示"
    })

    for e in all_data:
        e["last_updated"] = now
        
    # 去除重複網址或活動
    seen = set()
    unique_data = []
    for d in all_data:
        identifier = d['title'] + d['location']
        if identifier not in seen:
            unique_data.append(d)
            seen.add(identifier)
            
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
        
    print(f"任務完成！已透過文化部開放資料更新 {len(unique_data)} 筆活動檔案。")
