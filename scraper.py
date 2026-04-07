import requests
from bs4 import BeautifulSoup
import json
import datetime

# --- 地區判斷邏輯 ---
def get_region(text):
    text = text.upper()
    # 判斷北部
    if any(k in text for k in ['台北', '新北', '桃園', '基隆', 'LEGACY TAIPEI', 'ZEPP', '北流', '小巨蛋', '河岸留言', 'THE WALL', 'NUZONE']):
        return "北部"
    # 判斷中部
    if any(k in text for k in ['台中', '彰化', '雲林', 'LEGACY TAICHUNG', '迴響']):
        return "中部"
    # 判斷南部
    if any(k in text for k in ['高雄', '台南', '屏東', '嘉義', '駁二', '後台', '高流', '衛武營', 'LIVE WAREHOUSE']):
        return "南部"
    # 判斷東部
    if any(k in text for k in ['台東', '花蓮', '宜蘭', '鐵花村']):
        return "東部"
    return "全台/其他"

# --- 第一道大門分支 A：KKTIX 官方 API ---
def fetch_kktix():
    print("正在從 KKTIX API 抓取全站資料...")
    url = "https://kktix.com/events.json"
    results = []
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        for item in data.get('entry', []):
            title = item.get('title', '')
            # 過濾關鍵字，確保跟音樂或演出有關
            if any(k in title for k in ['演唱會', '音樂', '祭', 'Live', '巡迴', 'Tour', '專場', 'DJ', '派對']):
                results.append({
                    "title": title,
                    "location": item.get('content', '見網頁說明').split('地點: ')[-1].split('\n')[0],
                    "ticket_date": "請見網頁",
                    "link": item.get('url', ''),
                    "region": get_region(title + item.get('content', '')),
                    "source": "KKTIX"
                })
    except Exception as e:
        print(f"KKTIX 抓取失敗: {e}")
    return results

# --- 第一道大門分支 B：iNDIEVOX 爬蟲 ---
def fetch_indievox():
    print("正在從 iNDIEVOX 抓取資料...")
    url = "https://www.indievox.com/activity/list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    results = []
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 尋找所有的活動卡片
        events = soup.find_all('div', class_='col-md-4')
        for event in events:
            title_tag = event.find('h5')
            if title_tag:
                title = title_tag.text.strip()
                link = "https://www.indievox.com" + title_tag.find('a')['href']
                results.append({
                    "title": title,
                    "location": "詳情見售票網", 
                    "ticket_date": "請見網頁",
                    "link": link,
                    "region": get_region(title),
                    "source": "iNDIEVOX"
                })
    except Exception as e:
        print(f"iNDIEVOX 抓取失敗: {e}")
    return results

# --- 第二道大門：預留給 Accupass (目前為空) ---
def fetch_accupass():
    return []

# --- 第三道大門：預留給 PTT 或 音樂媒體 (目前為空) ---
def fetch_media():
    return []

# --- 主程式：整合所有資料並存檔 ---
if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 將所有爬蟲抓到的資料倒進大池子裡
    all_data = []
    all_data.extend(fetch_kktix())
    all_data.extend(fetch_indievox())
    all_data.extend(fetch_accupass())
    all_data.extend(fetch_media())
    
    # 加上統一的最後更新時間
    for e in all_data:
        e["last_updated"] = now
        
    if all_data:
        # 移除重複的活動 (以網址作為判斷標準)
        seen = set()
        unique_data = []
        for d in all_data:
            if d['link'] not in seen:
                unique_data.append(d)
                seen.add(d['link'])
        
        # 將最終資料寫入 data.json
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(unique_data, f, ensure_ascii=False, indent=4)
        print(f"任務完成！共整理出 {len(unique_data)} 筆全台演出資訊。")
