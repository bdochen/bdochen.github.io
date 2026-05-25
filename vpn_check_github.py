# vpn_check_github.py
import requests
import time
import os
import json

# ===================== 从环境变量读取配置 =====================
# 从 GitHub Secrets 读取企业微信 Key
QYWX_KEY = os.environ.get("QYWX_BOT_KEY", "")

# 从 GitHub Secrets 读取 Cookie 列表（JSON 格式字符串）
# 格式示例: '["cookie1", "cookie2"]'
cookie_list_str = os.environ.get("COOKIE_LIST", "[]")
try:
    cookie_list = json.loads(cookie_list_str)
except json.JSONDecodeError:
    print("错误：COOKIE_LIST 格式不正确，请使用 JSON 数组格式")
    cookie_list = []
# ============================================================

# 企业微信推送
def send_msg(title, content):
    if not QYWX_KEY:
        print("警告：QYWX_BOT_KEY 未设置，跳过推送")
        return
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={QYWX_KEY}"
    data = {"msgtype": "text", "text": {"content": f"{title}\n\n{content}"}}
    try:
        requests.post(url, json=data)
    except Exception as e:
        print(f"推送失败：{e}")

# Cookie 字符串转字典
def parse_cookie(s):
    return {k: v for k, v in (i.split("=", 1) for i in s.split("; ") if "=" in i)}

# 签到
def checkin(cookie, idx):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "referer": "https://ikuuu.win/user",
        "x-requested-with": "XMLHttpRequest"
    }
    try:
        res = requests.post("https://ikuuu.win/user/checkin", cookies=cookie, headers=headers, timeout=30)
        ret = res.json()
    except Exception as e:
        return f"账户{idx}：请求失败 - {str(e)}"
    
    email = cookie.get("email", "未知").replace("%40", "@")
    msg = ret.get("msg", "无返回")
    
    # 处理不同的返回结果
    if "msg" in ret:
        if "已签到" in ret["msg"]:
            msg = "✅ " + ret["msg"]
        elif "获得" in ret["msg"]:
            msg = "🎉 " + ret["msg"]
        else:
            msg = "ℹ️ " + ret["msg"]
    
    print(f"账户{idx} {email}：{msg}")
    return f"账户{idx}({email})：{msg}"

# 主程序
def main():
    if not cookie_list:
        print("错误：COOKIE_LIST 未设置或为空")
        send_msg("V签到失败", "COOKIE_LIST 环境变量未设置或格式错误")
        return
    
    print(f"共加载 {len(cookie_list)} 个账户")
    result_lines = []
    
    for i, cookie_str in enumerate(cookie_list, 1):
        print(f"\n--- 处理账户 {i} ---")
        cookie_dict = parse_cookie(cookie_str)
        result = checkin(cookie_dict, i)
        result_lines.append(result)
        if i < len(cookie_list):  # 最后一个不需要等待
            time.sleep(15)
    
    final_result = "\n\n".join(result_lines)
    print(f"\n签到完成！\n{final_result}")
    send_msg("V签到结果", final_result)

if __name__ == "__main__":
    main()
