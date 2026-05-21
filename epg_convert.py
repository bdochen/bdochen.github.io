import requests
import gzip
import xml.etree.ElementTree as ET
import re

# 配置
SOURCE_URL = "https://e.erw.cc/all.xml.gz"
STANDARD_URL = "http://47.110.243.216:51234/playback.xml"
OUTPUT_FILE = "playback.xml"

def clean_name(name):
    if not name:
        return ""
    name = name.strip()
    name = re.sub(r"\s+", "", name)
    name = re.sub(r"高清|超清|HD|综|CCTV|卫视|台", "", name)
    return name.lower()

def main():
    try:
        # 下载标准频道
        print("下载标准频道...")
        resp = requests.get(STANDARD_URL, timeout=20)
        resp.raise_for_status()
        std_root = ET.fromstring(resp.content)

        # 建立映射：简化名 → 标准全名
        name_map = {}
        valid_channels = set()

        for ch in std_root.findall("channel"):
            std_id = ch.get("id")
            if not std_id:
                continue
            valid_channels.add(std_id)
            key = clean_name(std_id)
            name_map[key] = std_id

        print(f"标准频道数量：{len(valid_channels)}")

        # 下载源 EPG
        print("下载源 EPG...")
        gz_resp = requests.get(SOURCE_URL, timeout=30)
        xml_content = gzip.decompress(gz_resp.content)
        root = ET.fromstring(xml_content)

        # 处理频道：替换 + 删除
        for ch in list(root.findall("channel")):
            cid = ch.get("id")
            key = clean_name(cid)
            if key in name_map:
                new_id = name_map[key]
                ch.set("id", new_id)
                dn = ch.find("display-name")
                if dn is not None:
                    dn.text = new_id
            else:
                root.remove(ch)

        # 处理节目：替换 + 删除
        for prog in list(root.findall("programme")):
            chan = prog.get("channel")
            key = clean_name(chan)
            if key in name_map:
                prog.set("channel", name_map[key])
            else:
                root.remove(prog)

        # 保存
        tree = ET.ElementTree(root)
        tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
        print(f"✅ 生成成功：{OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ 错误：{e}")
        exit(1)

if __name__ == "__main__":
    main()
