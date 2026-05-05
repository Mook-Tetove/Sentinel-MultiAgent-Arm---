import os
import sys
import threading
import importlib.util
import time
import re
import json
from datetime import datetime

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 脑区
router_agent = load_module("router", os.path.join(BASE_DIR, "2_Brain_Core", "router_agent.py"))
chat_agent = load_module("chat", os.path.join(BASE_DIR, "2_Brain_Core", "Agent_Workers", "chat_agent.py"))
code_agent = load_module("code", os.path.join(BASE_DIR, "2_Brain_Core", "Agent_Workers", "code_agent.py"))
openclaw_agent = load_module("openclaw", os.path.join(BASE_DIR, "2_Brain_Core", "Agent_Workers", "openclaw_agent.py"))
reminder_agent = load_module("reminder", os.path.join(BASE_DIR, "2_Brain_Core", "Agent_Workers", "reminder_agent.py"))

# 2. 感官
log_watcher = load_module("watcher", os.path.join(BASE_DIR, "1_Event_Listeners", "log_watcher.py"))
voice_speaker = load_module("speaker", os.path.join(BASE_DIR, "3_Action_Executors", "voice_speaker.py"))
voice_listener = load_module("listener", os.path.join(BASE_DIR, "1_Event_Listeners", "voice_listener.py"))
qq_receiver = load_module("qq_receiver", os.path.join(BASE_DIR, "1_Event_Listeners", "qq_receiver.py"))

# 3. 骨骼
serial_sender = load_module("serial", os.path.join(BASE_DIR, "4_Hardware_Link", "serial_sender.py"))

# ================= 🚨 终极修复：逆向反馈：屏幕触摸唤醒 =================
def on_screen_touch():
    """当 ESP32 屏幕被触摸时，直接按响耳朵的唤醒门铃"""
    print("\n[系统总线] 👆 屏幕被触摸，通知耳朵强行唤醒...")
    voice_listener.trigger_physical_wake()

# 把大脑的回调挂载到躯体上！
serial_sender.robot_arm.on_touch_callback = on_screen_touch
# =========================================================

def extract_and_execute_actions(text):
    actions = re.findall(r'<action:\s*(\w+)>', text)
    for act in actions:
        if act == "shake_head":
            act = "shake"
        elif act == "nod_head":
            act = "nod"
            
        if act == "retract":
            continue 
            
        serial_sender.robot_arm.send_action(act)
        
        if act == "shake":
            time.sleep(1.5) 
        elif act == "nod":
            time.sleep(1.0) 
        else:
            time.sleep(0.5) 
            
    clean_text = re.sub(r'<action:\s*\w+>', '', text)
    return clean_text.strip()

def clean_text_for_speech(text):
    clean_text = re.sub(r'```.*?```', '代码已经发送到屏幕上。', text, flags=re.DOTALL)
    clean_text = clean_text.replace('*', '').replace('#', '')
    return clean_text

def process_user_input(user_text):
    serial_sender.robot_arm.send_action("extend")
    serial_sender.robot_arm.print_screen("系统状态", "正在进行意图路由分析...")
    
    print("\n[系统总线] 正在进行意图路由分析...")
    intent = router_agent.analyze_intent(user_text)
    target = intent.get("target")

    agent_name_map = {
        "chat_agent": "情感陪聊中枢",
        "code_agent": "后台算力引擎",
        "openclaw_agent": "前台物理外骨骼",
        "reminder_agent": "时间日程管家"
    }
    display_name = agent_name_map.get(target, "未知决策中枢")
    
    print(f"[系统总线] 路由决策完毕 -> 分发至: {target} ({display_name})")
    serial_sender.robot_arm.print_screen("中枢唤醒", display_name)
    
    text_without_actions = ""
    
    if target == "chat_agent":
        raw_reply = chat_agent.handle_chat(user_text)
        text_without_actions = extract_and_execute_actions(raw_reply)
        
        if any(word in text_without_actions for word in ["好", "是", "没问题", "对"]):
            serial_sender.robot_arm.send_action("nod")
        elif any(word in text_without_actions for word in ["不", "错", "没有"]):
            serial_sender.robot_arm.send_action("shake")
            
        print(f"🤖 [哨兵]: {text_without_actions}\n")
        serial_sender.robot_arm.print_screen("聊天回复", clean_text_for_speech(text_without_actions))
        voice_speaker.speak_text(clean_text_for_speech(text_without_actions))
        
    elif target == "code_agent":
        result = code_agent.handle_code_task(user_text)
        text_without_actions = extract_and_execute_actions(result['ai_thought'])
        
        if result['has_code']:
            if result['execution_status'] == "success":
                serial_sender.robot_arm.send_action("nod")
                serial_sender.robot_arm.print_screen("执行成功", result['execution_output'][:150] + "...") # 防极端报错过长
                voice_speaker.speak_text("代码执行完毕")
            else:
                serial_sender.robot_arm.send_action("shake")
                serial_sender.robot_arm.print_screen("代码报错", "查看终端日志")
                voice_speaker.speak_text("代码在沙箱里报错了。")
        else:
            serial_sender.robot_arm.print_screen("分析结果", clean_text_for_speech(text_without_actions))
            voice_speaker.speak_text(clean_text_for_speech(text_without_actions))
        
    elif target == "openclaw_agent":
        raw_reply = openclaw_agent.handle_openclaw_task(user_text)
        text_without_actions = extract_and_execute_actions(raw_reply)
        serial_sender.robot_arm.send_action("nod")
        serial_sender.robot_arm.print_screen("操作结果", clean_text_for_speech(text_without_actions))
        voice_speaker.speak_text(clean_text_for_speech(text_without_actions))
        
    elif target == "reminder_agent":
        raw_reply = reminder_agent.handle_reminder_task(user_text)
        text_without_actions = extract_and_execute_actions(raw_reply)
        
        print(f"🤖 [哨兵管家]: {text_without_actions}\n")
        serial_sender.robot_arm.print_screen("日程查询", clean_text_for_speech(text_without_actions))
        voice_speaker.speak_text(clean_text_for_speech(text_without_actions))
        
    if text_without_actions:
        dynamic_time = min(60, max(5, len(text_without_actions) * 0.25 + 2))
        print(f"\n[系统总线] 动态休眠: 共 {len(text_without_actions)} 字，机甲将保持展示 {dynamic_time:.1f} 秒...")
        time.sleep(dynamic_time) 
        
    serial_sender.robot_arm.send_action("standby") # 🚨 聊完天恢复平视待机
    serial_sender.robot_arm.print_screen("SENTINEL", "STANDBY")

def handle_voice_command(voice_text):
    if voice_text == "[JUST_WAKE]":
        serial_sender.robot_arm.send_action("extend")
        serial_sender.robot_arm.print_screen("待命", "我在听...")
        voice_speaker.speak_text("我在。")
        return
    process_user_input(voice_text)

def handle_xray_log(xray_text):
    """专门处理觉醒时的实时字幕流"""
    display_text = xray_text if len(xray_text) < 20 else "..." + xray_text[-17:]
    serial_sender.robot_arm.print_screen("正在倾听", display_text)

def handle_background_error(error_msg):
    serial_sender.robot_arm.send_action("extend")
    serial_sender.robot_arm.send_action("shake")
    serial_sender.robot_arm.print_screen("🚨 异常警告", error_msg)
    voice_speaker.speak_text("检测到后台报错。")

def handle_qq_message(sender, text, msg_type):
    # 修复你之前残留的 text_without_actions 未定义报错
    serial_sender.robot_arm.send_action("extend") 
    serial_sender.robot_arm.print_screen(f"QQ: {sender}", text)
    voice_speaker.speak_text(f"收到来自 {sender} 的QQ消息。")

    dynamic_time = min(60, max(5, len(text) * 0.25 + 2))
    print(f"\n[QQ 雷达] 动态休眠: 消息共 {len(text)} 字，机甲将保持展示 {dynamic_time:.1f} 秒...")
    
    time.sleep(dynamic_time) 
    serial_sender.robot_arm.send_action("standby")
    serial_sender.robot_arm.print_screen("SENTINEL", "STANDBY")

def check_time_events():
    reminders_path = os.path.join(BASE_DIR, "reminders.json")
    while True:
        try:
            if os.path.exists(reminders_path):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                with open(reminders_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                alarms_modified = False
                for alarm in data.get("alarms", [])[:]:
                    if alarm["time"].startswith(now_str):
                        serial_sender.robot_arm.send_action("extend")
                        serial_sender.robot_arm.print_screen("⏰ 准时提醒", alarm["task"])
                        voice_speaker.speak_text(f"老板，时间到了。该准备：{alarm['task']}")
                        
                        data["alarms"].remove(alarm)
                        alarms_modified = True
                
                if alarms_modified:
                    with open(reminders_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    
                    time.sleep(10)
                    serial_sender.robot_arm.send_action("standby")
                    serial_sender.robot_arm.print_screen("SENTINEL", "STANDBY")
        except Exception:
            pass 
        time.sleep(60)

if __name__ == "__main__":
    print("===================================================")
    print("      🧠 哨兵系统 (听觉触觉完全体) 正在启动... ")
    print("===================================================")
    
    real_log_path = os.path.join(BASE_DIR, "dev_error.log")
    threading.Thread(target=lambda: log_watcher.watch_logs(real_log_path, handle_background_error), daemon=True).start()
    
    qq_ws_url = "ws://127.0.0.1:3002" 
    threading.Thread(target=lambda: qq_receiver.watch_qq_messages(qq_ws_url, handle_qq_message), daemon=True).start()
    
    threading.Thread(target=check_time_events, daemon=True).start()
    
    # 🚨 终极修复：必须启动语音监听线程，并把【文字回调】和【实时X光回调】都插好！
    threading.Thread(target=lambda: voice_listener.start_listening(
        on_text_callback=handle_voice_command,
        on_xray_callback=handle_xray_log
    ), daemon=True).start()
    
    time.sleep(2)
    voice_speaker.speak_text("系统已上线。")
    serial_sender.robot_arm.send_action("standby") # 保持趴下但屏幕平视
    # 🚨 核心修复：直接发 STANDBY，触发底层画眼睛！
    serial_sender.robot_arm.print_screen("SENTINEL", "STANDBY")
    
    while True:
        try:
            user_input = input("\n>> [mookt]: ").strip()
            if not user_input: continue
            
            if user_input.lower() in ['exit', 'quit', 'shutdown', '关机']:
                print("[系统总线] 正在执行关机程序，物理躯体正在收回...")
                serial_sender.robot_arm.send_action("retract")
                voice_speaker.speak_text("切断电源，关机。")

                  # 🚨 关键：等 1.5 秒，让机甲完全趴下后，再关闭程序！
                time.sleep(3) 
                os._exit(0)
                
            process_user_input(user_input)
            
        except KeyboardInterrupt:
            break