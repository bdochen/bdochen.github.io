import requests
import gzip
import xml.etree.ElementTree as ET
import re

# ===================== 配置项 =====================
# 源EPG压缩包地址
SOURCE_URL = "https://e.erw.cc/all.xml.gz"
# 标准频道列表地址（你的epg.txt）
STANDARD_XML_URL = "http://47.110.243.216:51234/playback.xml"
# 输出文件名
OUTPUT_FILE = "playback.xml"
# ==================================================

def main():
    session = requests.Session()
    # 1. 下载标准频道列表（epg.txt 替换为网络下载）
    print("正在下载标准频道列表...")
    standard_resp = session.get(STANDARD_XML_URL, timeout=30)
    standard_resp.raise_for_status()
    
    # 解析标准XML，提取所有 channel id，自动生成映射表
    standard_root = ET.fromstring(standard_resp.content)
    standard_channels = {}
    for ch in standard_root.findall("channel"):
        ch_id = ch.get("id")
        if ch_id:
            standard_channels[ch_id] = ch_id  # 自动生成 name_map：原名=标准名

    valid_ids = set(standard_channels.keys())
    print(f"加载完成：共 {len(valid_ids)} 个标准频道")

    # 2. 下载并解压源EPG
    print("正在下载源EPG数据...")
    gz_resp = session.get(SOURCE_URL, timeout=60)
    gz_resp.raise_for_status()

    # 解压XML
    xml_content = gzip.decompress(gz_resp.content)
    root = ET.fromstring(xml_content)

    # 3. 清理无用频道（只保留标准列表里的）
    print("清理无效频道...")
    for channel in list(root.findall("channel")):
        cid = channel.get("id")
        if cid not in valid_ids:
            root.remove(channel)
        else:
            # 自动替换为标准名称
            new_name = standard_channels[cid]
            channel.set("id", new_name)
            display_name = channel.find("display-name")
            if display_name is not None:
                display_name.text = new_name

    # 4. 清理无用节目单
    print("清理无效节目数据...")
    for programme in list(root.findall("programme")):
        p_channel = programme.get("channel")
        if p_channel not in valid_ids:
            root.remove(programme)
        else:
            programme.set("channel", standard_channels[p_channel])

    # 5. 保存最终XML
    tree = ET.ElementTree(root)
    tree.write(
        OUTPUT_FILE,
        encoding="utf-8",
        xml_declaration=True,
        method="xml"
    )
    print(f"✅ 处理完成！已生成 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
