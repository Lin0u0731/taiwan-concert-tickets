import requests
import json
import datetime
import xml.etree.ElementTree as ET # 🌟 召喚專門解析 RSS 的內建神器

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

# 🎸 修正版：Blow 吹音樂 RSS 爬蟲
def fetch_blow_music():
    print("正在從『Blow 吹音樂』抓取...")
    url = "https://blow.streetvoice.com/feed/"
    results = []
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        
        # 🌟 使用正確的 XML 解析器，網址再也不會被吃掉了！
        root = ET.fromstring(resp.content)
        for item in root.findall('.//item'):
            title = item.findtext('title') or ""
            link = item.findtext('link') or ""
            
            # 放寬關鍵字，多抓一點情報
            if any(k in title for k in ['專場', '音樂祭', '開唱', '巡演', '演唱會', '售票', '陣容', 'Live', '發片', '來台']):
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

# 🏛️ 修正版：文化部資料 (移除過度嚴格的過濾)
def fetch_culture_api():
    print("正在抓取文化部開放資料...")
    url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=5"
    results = []
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        
        # 抓取前 40 筆資料讓網頁豐富起來
        for item in data[:40]:
            title = item.get("title", "")
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
                "source": "政府公開資料 (OPENTIX 等)"
            })
    except Exception as e:
        print(f"文化部 API 失敗: {e}")
    return results

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_data = []
    
    all_data.extend(fetch_blow_music())
    all_data.extend(fetch_culture_api())

    for e in all_data:
        e["last_updated"] = now
        
    # 🌟 升級防重複機制：用「標題+網址」來判斷，更準確！
    seen = set()
    unique_data = []
    for d in all_data:
        identifier = d['title'] + d['link']
        if identifier not in seen:
            unique_data.append(d)
            seen.add(identifier)
            
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
        
    print(f"任務完成！已成功抓取並更新 {len(unique_data)} 筆資料。")
