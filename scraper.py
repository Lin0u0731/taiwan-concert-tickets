import requests
from bs4 import BeautifulSoup
import json
import datetime
import xml.etree.ElementTree as ET

def get_region(text):
    text = text.upper()
    # 稍微豐富一下地區的關鍵字庫
    if any(k in text for k in ['台北', '新北', '桃園', '基隆', 'LEGACY TAIPEI', 'ZEPP', '北流', '小巨蛋', '河岸留言', 'THE WALL', 'NUZONE', '樂悠悠之口', '女巫店']):
        return "北部"
    if any(k in text for k in ['台中', '彰化', '雲林', 'LEGACY TAICHUNG', '迴響', '圓滿戶外']):
        return "中部"
    if any(k in text for k in ['高雄', '台南', '屏東', '嘉義', '駁二', '後台', '高流', '衛武營', 'LIVE WAREHOUSE']):
        return "南部"
    if any(k in text for k in ['台東', '花蓮', '宜蘭', '鐵花村']):
        return "東部"
    return "全台/其他"

# 🎸 X光透視版：Blow 吹音樂情報萃取
def fetch_blow_music():
    print("正在從『Blow 吹音樂』抓取並透視內文...")
    url = "https://blow.streetvoice.com/feed/"
    results = []
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        root = ET.fromstring(resp.content)
        
        for item in root.findall('.//item'):
            title = item.findtext('title') or ""
            news_link = item.findtext('link') or ""
            
            # 🌟 啟動 X 光機：抓取隱藏在 RSS 裡的「完整文章內文」
            content_elem = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
            content = content_elem.text if content_elem is not None else (item.findtext('description') or "")
            
            if any(k in title for k in ['專場', '音樂祭', '開唱', '巡演', '演唱會', '售票', '陣容', 'Live', '發片', '來台']):
                
                real_ticket_link = news_link
                ticket_source = "Blow 吹音樂 (情報)"
                
                # 🌟 網址小偷：剖開內文，把真正的售票網址挖出來！
                if content:
                    soup = BeautifulSoup(content, "html.parser")
                    for a_tag in soup.find_all('a'):
                        href = a_tag.get('href', '')
                        if 'kktix.com' in href:
                            real_ticket_link = href
                            ticket_source = "KKTIX"
                            break
                        elif 'indievox.com' in href:
                            real_ticket_link = href
                            ticket_source = "iNDIEVOX"
                            break
                        elif 'tixcraft.com' in href:
                            real_ticket_link = href
                            ticket_source = "拓元售票"
                            break
                        elif 'ticketplus.com.tw' in href:
                            real_ticket_link = href
                            ticket_source = "遠大售票"
                            break
                        elif 'ibon.com.tw' in href:
                            real_ticket_link = href
                            ticket_source = "ibon售票"
                            break
                            
                results.append({
                    "title": title,
                    "location": "詳見售票網頁",
                    "ticket_date": "點擊前往售票網頁",
                    "link": real_ticket_link,
                    # 🌟 地區雷達：把標題跟「完整內文」加起來一起判斷地區！
                    "region": get_region(title + content),
                    "source": ticket_source
                })
    except Exception as e:
        print(f"Blow 吹音樂 抓取失敗: {e}")
    return results

# 🏛️ 文化部資料保持不變
def fetch_culture_api():
    print("正在抓取文化部開放資料...")
    url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=5"
    results = []
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        
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
                "source": "政府公開資料"
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
        
    seen = set()
    unique_data = []
    for d in all_data:
        identifier = d['title'] + d['link']
        if identifier not in seen:
            unique_data.append(d)
            seen.add(identifier)
            
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
        
    print(f"任務完成！已成功萃取 {len(unique_data)} 筆精準資料。")
