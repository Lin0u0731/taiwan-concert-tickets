import json
import datetime

# 這是一個測試版的資料產生器，用來模擬爬蟲抓回來的資料
def get_mock_data():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    events = [
        {
            "title": "大港開唱 Megaport Festival",
            "artist": "多組藝人",
            "date": "2026-03-28",
            "ticket_date": "2026-01-15 12:00:00",
            "link": "https://kktix.com/",
            "source": "KKTIX 模擬資料",
            "last_updated": now
        },
        {
            "title": "五月天跨年演唱會",
            "artist": "五月天",
            "date": "2026-12-31",
            "ticket_date": "2026-11-01 11:00:00",
            "link": "https://tixcraft.com/",
            "source": "拓元 模擬資料",
            "last_updated": now
        }
    ]
    return events

if __name__ == "__main__":
    data = get_mock_data()
    # 將資料寫入 data.json 檔案
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("資料更新成功！已生成 data.json")
