import json
import os
import re
from datetime import datetime
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_PATH = os.path.join(BASE_DIR, "reminders.json")

def auto_save_alarm(user_text):
    """
    语义解析引擎：升级版，支持“X月Y日/号”
    """
    # 匹配 X月Y号 或 X月Y日
    date_match = re.search(r'(\d+)月(\d+)[号日]', user_text)
    if not date_match:
        date_match = re.search(r'(\d+)\.(\d+)', user_text)
    
    if date_match:
        # 🚨 防呆设计：如果用户是在问天数，千万别当成存闹钟！
        if any(word in user_text for word in ["多久", "几天", "天数", "多少天", "第"]):
            return False, ""

        month = date_match.group(1).zfill(2)
        day = date_match.group(2).zfill(2)
        year = datetime.now().year
        
        task = re.sub(r'(\d+)[月\.].*?[号日\s]?', '', user_text).strip()
        task = task.replace("提醒我", "").replace("要", "").replace("干", "")
        
        if not task: task = "未命名任务"
        
        target_time = f"{year}-{month}-{day} 09:00:00"
        
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            data["alarms"].append({"time": target_time, "task": task})
            
            with open(PROFILE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True, f"好的老板，已存入矩阵。{month}月{day}日我会准时提醒你：{task}"
        except Exception as e:
            return False, f"写入失败: {e}"
    
    return False, ""

def handle_reminder_task(user_text):
    """
    处理查询和自动保存 (高智商版)
    """
    # 1. 尝试自动保存任务
    success, feedback = auto_save_alarm(user_text)
    if success:
        return feedback + " <action: nod>"

    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return "备忘录文件读取失败。"

    now = datetime.now()
    
    # 🚨 2. 纪念日天数查询 (同义词联想版)
    if any(word in user_text for word in ["多久", "几天", "天数", "多少天", "第"]):
        for item in data.get("anniversaries", []):
            name = item["name"]
            
            # 提取核心词：去掉“纪念日”三个字，比如“确定关系纪念日”变成“确定关系”
            core_name = name.replace("纪念日", "") 
            
            # 建立同义词库（你可以自己在这里无限加黑话）
            synonyms = [core_name]
            if core_name == "确定关系":
                synonyms.extend(["在一起", "恋爱", "处对象"])
            elif core_name == "认识":
                synonyms.extend(["相识", "加好友"])
                
            # 只要用户的话里包含同义词库里的任何一个词，瞬间命中！
            if any(syn in user_text for syn in synonyms):
                start_date = datetime.strptime(item["date"], "%Y-%m-%d")
                delta = now - start_date
                return f"报告老板，今天是你们{name}的第 {delta.days} 天。<action: nod>"
                
    # 3. 生日查询逻辑
    if "生日" in user_text:
        for item in data.get("anniversaries", []):
            if item.get("type") == "birthday":
                bday = datetime.strptime(item["date"], "%Y-%m-%d")
                this_year_bday = bday.replace(year=now.year)
                days_left = (this_year_bday - now).days
                
                # 如果今年生日过了，算明年的
                if days_left < 0: 
                    this_year_bday = this_year_bday.replace(year=now.year + 1)
                    days_left = (this_year_bday - now).days
                    
                if days_left == 0:
                    return f"老板，今天就是对象的生日！赶紧去庆祝！<action: nod>"
                else:
                    return f"老板，对象生日是 8月8日，距离下次生日还有 {days_left} 天，记得提前准备礼物。<action: nod>"

    return "你要提醒我什么？请说具体的日期，比如“5月1号要出去旅游”。"