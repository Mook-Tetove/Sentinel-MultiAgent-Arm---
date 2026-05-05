import json
import time
import websocket
import threading

def watch_qq_messages(ws_url, callback):
    """工业级 QQ 监听雷达：对接 NapCatQQ"""
    print(f"📡 [QQ 监听雷达] 正在扫描底层消息总线: {ws_url}")

    def on_message(ws, message):
        try:
            data = json.loads(message)
            if data.get('post_type') == 'message':
                msg_type = data.get('message_type') 
                raw_text = data.get('raw_message', '')
                sender_info = data.get('sender', {})
                sender_name = sender_info.get('card') or sender_info.get('nickname') or '未知好友'

                # 忽略表情包CQ码和空消息
                if raw_text.strip() and not raw_text.startswith('[CQ:'):
                    print(f"\n💬 [QQ 截获] {sender_name}: {raw_text}")
                    callback(sender_name, raw_text, msg_type)
        except Exception:
            pass

    def on_error(ws, error):
        # 静默底层网络报错，保持终端干净
        pass

    def on_close(ws, close_status_code, close_msg):
        # 移交到外部循环去提示状态
        pass

    def run_ws():
        max_retries = 2  # 🚨 设定最大尝试次数为 2 次
        retry_count = 0

        while retry_count < max_retries:
            ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close)
            
            # 阻塞运行：如果没开 QQ，这句会立刻失败并往下执行
            ws.run_forever()
            
            retry_count += 1
            if retry_count < max_retries:
                print(f"⚠️ [QQ 监听雷达] 未检测到 NapCatQQ，2秒后进行第 {retry_count + 1} 次尝试...")
                time.sleep(2)
                
        # 🚨 试满 2 次后跳出循环，彻底放弃
        print("🛑 [QQ 监听雷达] 尝试失败，QQ 雷达已静默休眠，主系统继续正常运行！")

    # 依然放在后台线程跑，就算放弃了也绝对不会卡死主系统
    threading.Thread(target=run_ws, daemon=True).start()