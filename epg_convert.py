import requests
import gzip
import xml.etree.ElementTree as ET
import re

# 配置
SOURCE_URL = "https://e.erw.cc/all.xml.gz"
# 从你服务器下载标准频道表
STANDARD_URL = "http://47.110.243.216:51234/playback.xml"
OUTPUT_FILE = "playback.xml"

def clean(s):
    """简化匹配：去掉空格、高清、HD、综合等"""
    return re.sub(r"[\s高清超清HD综]", "", s.lower())

def main():
    sess = requests.Session()

    # 1. 下载标准频道（你的服务器）
    print("下载标准频道表...")
    std_resp = sess.get(STANDARD_URL, timeout=30)
    std_resp.raise_for_status()
    std_root = ET.fromstring(std_resp.content)

    # 构建映射：短名 → 标准全名（CCTV1 → CCTV1综合）
    name_map = {}
    valid_ids = set()
    for ch in std_root.findall("channel"):
        full = ch.get("id")
        if not full:
            continue
        valid_ids.add(full)
        short = clean(full)
        name_map[short] = full

    print(f"标准频道：{len(valid_ids)} 个")

    # 2. 下载并解压源EPG
    print("下载源EPG...")
    gz_resp = sess.get(SOURCE_URL, timeout=60)
    gz_resp.raise_for_status()
    xml_data = gzip.decompress(gz_resp.content)
    root = ET.fromstring(xml_data)

    # 3. 过滤并替换频道
    for ch in list(root.findall("channel")):
        cid = ch.get("id")
        if not cid:
            root.remove(ch)
            continue
        key = clean(cid)
        if key in name_map:
            new_id = name_map[key]
            ch.set("id", new_id)
            dn = ch.find("display-name")
            if dn is not None:
                dn.text = new_id
        else:
            root.remove(ch)

    # 4. 过滤并替换节目
    for prog in list(root.findall("programme")):
        cid = prog.get("channel")
        if not cid:
            root.remove(prog)
            continue
        key = clean(cid)
        if key in name_map:
            prog.set("channel", name_map[key])
        else:
            root.remove(prog)

    # 5. 保存
    tree = ET.ElementTree(root)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"✅ 已生成 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
