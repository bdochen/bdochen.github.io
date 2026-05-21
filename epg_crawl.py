import requests

# 爬取 XML 并保存
def main():
    url = "http://47.110.243.216:51234/playback.xml"
    
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        
        with open("playback.xml", "wb") as f:
            f.write(resp.content)
            
        print("✅ 爬取成功：playback.xml")
        
    except Exception as e:
        print(f"❌ 爬取失败：{e}")
        exit(1)

if __name__ == "__main__":
    main()
