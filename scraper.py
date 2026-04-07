import requests
from bs4 import BeautifulSoup
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

# 🎸 新增情報源：Blow 吹音樂 (台灣最大獨立音樂情報站)
def fetch_blow_music():
    print("正在從『Blow 吹音樂』抓取獨立音樂售票情報...")
    url = "https://blow.streetvoice.com/feed/" # 這是他們公開的 RSS 通道
    results = []
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        # 用 BeautifulSoup 解析 XML
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # RSS 的每一篇文章都包在 <item> 裡面
        for item in soup.find_all("item"):
            title = item.title.text if item.title else ""
            link = item.link.text if item.link else ""
            
            # 篩選關鍵字：確保這篇新聞是關於演出的
            if any(k in title for k in ['專場', '音樂祭', '開唱', '巡演', '演唱會', '售票', '陣容', 'Live']):
                results.append({
                    "title": title,
                    "location": "詳見情報內文",
                    "ticket_date": "點擊查看售票詳情",
                    "link": link,
                    "region": get_region(title),
                    "source": "Blow 吹音樂 (情報)"
                })
    except Exception as e:
        print(f"Blow 吹音樂 抓取失敗: {e}")
    return results

# 🏛️ 文化部資料 (加上嚴格過濾器，過濾掉純戲劇/藝術展演)
def fetch_culture_api():
    print("正在抓取文化部開放資料...")
    url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=5"
    results = []
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        
        for item in data[:100]:
            title = item.get("title", "")
            # 🌟 嚴格把關：只要標題看起來像樂團或音樂祭的！
            if not any(k in title for k in ['演唱會', '音樂祭', 'Live', '專場', '巡迴']):
                continue # 如果沒有這些關鍵字，就跳過不抓！
                
            show_info = item.get("showInfo", [])
            if not show_info: continue
                
            first_show = show_info[0]
            location = first_show.get("locationName", "未提供地點")
            time = first_show.get("time", "請見網頁公告")
            
            link = item.get("sourceWebPromote", "")
            if not link or not link.startswith("http"):
                link = "https://cloud.culture.tw/"
                
            results.append({
                "title": title,
                "location": location,
                "ticket_date": f"演出時間：{time}",
                "link": link,
                "region": get_region(title + location),
                "source": "政府公開資料"
            })
    except Exception as e:
        print(f"文化部 API 失敗: {e}")
    return results

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_data = []
    
    # 雙管齊下！
    all_data.extend(fetch_blow_music())
    all_data.extend(fetch_culture_api())

    for e in all_data:
        e["last_updated"] = now
        
    seen = set()
    unique_data = []
    for d in all_data:
        if d['link'] not in seen:
            unique_data.append(d)
            seen.add(d['link'])
            
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
        
    print(f"任務完成！已為聽團仔更新 {len(unique_data)} 筆最純的音樂情報。")
