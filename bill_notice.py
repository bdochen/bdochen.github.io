import os
import json
import requests
from datetime import datetime, timedelta

# 环境变量读取
QYWX_BOT_KEY = os.getenv("QYWX_BOT_KEY", "")
DISABLE_PUSH = os.getenv("DISABLE_PUSH", "false").lower() == "true"

try:
    REMINDER_CONFIG = json.loads(os.getenv("REMINDER_CONFIG", "[]"))
except Exception:
    print("REMINDER_CONFIG JSON 解析失败")
    REMINDER_CONFIG = []

def wecom_bot(title: str, content: str) -> None:
    if DISABLE_PUSH:
        print(f"[禁用推送] {title}\n{content}")
        return
    if not QYWX_BOT_KEY:
        print("未配置 QYWX_BOT_KEY，跳过推送")
        return

    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={QYWX_BOT_KEY}"
    data = {
        "msgtype": "text",
        "text": {"content": f"{title}\n\n{content}", "mentioned_list": ["@all"]}
    }
    try:
        r = requests.post(url, json=data, timeout=15)
        print("推送成功" if r.json().get("errcode") == 0 else f"推送失败: {r.text}")
    except Exception as e:
        print(f"推送异常: {e}")

def get_tomorrow_due_reminders():
    tomorrow_day = (datetime.now() + timedelta(days=1)).day
    items = [x for x in REMINDER_CONFIG if x.get("due_day") == tomorrow_day]
    if not items:
        return None
    lines = [f"📅 明日还款提醒（{(datetime.now()+timedelta(days=1)).strftime('%m月%d日')}）", "-"*30]
    for it in items:
        lines.append(f"{it['name']} - {it['amount']}")
    return "\n".join(lines)

def get_today_due_reminders():
    today_day = datetime.now().day
    items = [x for x in REMINDER_CONFIG if x.get("due_day") == today_day]
    if not items:
        return None
    lines = [f"⚠️ 当日还款提醒（{datetime.now().strftime('%m月%d日')}）", "-"*30]
    for it in items:
        lines.append(f"{it['name']} - {it['amount']}")
    lines.append("\n💡 今日到期请及时还款，避免逾期！")
    return "\n".join(lines)

def send_reminder():
    print(f"{datetime.now()} - 执行还款提醒任务")
    tomorrow_msg = get_tomorrow_due_reminders()
    if tomorrow_msg:
        wecom_bot("💳 还款提醒", tomorrow_msg)
    today_msg = get_today_due_reminders()
    if today_msg:
        wecom_bot("🔔 紧急还款提醒", today_msg)

if __name__ == "__main__":
    send_reminder()
