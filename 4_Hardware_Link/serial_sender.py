import serial
import json
import time
import threading

class SentinelHardware:
    def __init__(self, port="COM5", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.on_touch_callback = None 
        self.connect()

    def connect(self):
        try:
            # 开启 USB CDC 后的纯净连接，write_timeout 防抱死
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1, write_timeout=1.0)
            
            # S3 原生 USB 需要这两个信号保持高电平以维持通讯
            self.ser.dtr = True
            self.ser.rts = True
            
            print(f"[硬件链路] 已成功连接到哨兵躯体 ({self.port})")
            time.sleep(1) # 稍微等一下下
            self.ser.reset_input_buffer() 
            
            # 开启触摸监听神经
            threading.Thread(target=self._listen_to_esp32, daemon=True).start()
        except Exception as e:
            print(f"[硬件链路 警告] 无法连接到 {self.port}，降级为模拟模式！报错: {e}")

    def send_action(self, action_name):
        if self.ser and self.ser.is_open:
            data = {"cmd": "action", "val": action_name}
            json_str = json.dumps(data, ensure_ascii=False) + "\n"
            try:
                self.ser.write(json_str.encode('utf-8'))
                print(f"  -> [物理下发] 动作: {action_name}")
            except Exception as e:
                print(f"\n[⚠️ 串口堵塞] 肌肉指令发送失败，跳过本次动作！")
        else:
            print(f"  -> [模拟下发] 动作: {action_name}")

    def print_screen(self, sender, message):
        max_chars = 27  # 每行最多 27 个字
        max_lines = 7   # 🚨 屏幕 Y 轴极限：最多显示 7 行
        
        # 1. 先把消息里自带的换行符切开
        raw_lines = message.split('\n')
        
        display_lines = []
        for line in raw_lines:
            # 如果大模型发来的是空行，保留一个空占位
            if not line.strip():
                display_lines.append("")
                continue
                
            # 把每一长行按 22 个字切块，模拟屏幕的自动换行
            wrapped = [line[i:i+max_chars] for i in range(0, len(line), max_chars)]
            display_lines.extend(wrapped)
            
        # 2. 🚨 核心视网膜保护：超过 7 行，强行截断！
        if len(display_lines) > max_lines:
            # 留出前 6 行的内容
            display_lines = display_lines[:max_lines - 1]
            # 第 7 行统一变成省略号
            display_lines.append("... (内容过长，请看终端)")
            
        # 重新组合成发给硬件的最终字符串
        final_msg = "\n".join(display_lines)
        
        if self.ser and self.ser.is_open:
            data = {"cmd": "print", "sender": sender, "msg": final_msg}
            json_str = json.dumps(data, ensure_ascii=False) + "\n"
            try:
                self.ser.write(json_str.encode('utf-8'))
                print(f"  -> [物理下发] 屏幕: {sender} | (执行 {max_lines} 行安全排版)")
            except Exception as e:
                print(f"\n[⚠️ 串口堵塞] 屏幕指令发送失败: {e}")
        else:
            print(f"  -> [模拟下发] 屏幕: {sender} | {final_msg}")

    def _listen_to_esp32(self):
        """全频段监听：不管 ESP32 说啥，全给我在终端打出来！"""
        while self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if line.startswith("{") and '"event":"touch"' in line:
                        print(f"\n👆 [躯体反馈] 检测到屏幕被触摸！")
                        if self.on_touch_callback:
                            self.on_touch_callback()
                    else:
                        # 🚨 核心改动：把 ESP32 打印的所有废话、报错全显示出来！
                        print(f"🤖 [机甲底层原声]: {line}") 
            except Exception:
                pass
            time.sleep(0.01)

robot_arm = SentinelHardware(port="COM5")