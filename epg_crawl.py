import requests

# 目标 XML 地址
url = "http://47.110.243.216:51234/playback.xml"

# 爬取并保存
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # 请求失败会抛出异常

    # 写入本地文件
    with open("playback.xml", "wb") as f:
        f.write(response.content)

    print("✅ 爬取成功：playback.xml 已更新")

except Exception as e:
    print(f"❌ 爬取失败：{e}")
    exit(1)
