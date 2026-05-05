import os
import subprocess
import threading
import re

def clean_for_tts(text):
    """
    清洗文本，防止特殊符号把命令行卡死
    """
    # 删掉可能引起命令行崩溃的特殊字符（保留中英文字母、数字和常见标点）
    safe_text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、：；,.?!:]', ' ', text)
    return safe_text.strip()

def speak_text(text):
    # 洗干净要说的话
    safe_text = clean_for_tts(text)
    if not safe_text:
        return

    print(f"🔊 [发声器官启动]: 准备播报音频...")
    
    # ==========================================
    # 🎧 音色控制台（你想换谁的声音，就把 VOICE 改成谁）
    # ==========================================
    # zh-CN-YunxiNeural    （干练青年男声 - 默认特工音）
    # zh-CN-XiaoxiaoNeural （温柔知性女声 - 像微软小娜）
    # zh-CN-YunjianNeural  （深沉成熟男声 - 像纪录片旁白）
    # zh-CN-XiaoyiNeural   （活泼可爱小女孩）
    # zh-TW-HsiaoChenNeural（软萌台湾腔女声）
    
    VOICE = "zh-CN-XiaoxiaoNeural"  # 我先给你换个温柔女声试试
    
    def play_voice():
        try:
            # 加上 shell=True 解决 Windows 的各种抽风问题
            # 加上 text=True 让我们能读懂报错
            cmd = f'edge-playback --voice {VOICE} --text "{safe_text}"'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True 
            )
            
            # 【终极抓虫】：如果它敢不出声，就把它的报错死死钉在屏幕上！
            if result.returncode != 0:
                print(f"\n❌ [发声器官 罢工了]:")
                print(f"错误原因: {result.stderr.strip()}")
                
        except Exception as e:
            print(f"\n❌ [发声器官 彻底崩溃]: {e}")
            
    threading.Thread(target=play_voice, daemon=True).start()

# ==========================================
# 独立测试块
# ==========================================
if __name__ == "__main__":
    print("=== 发声器官 2.0 测试 ===")
    test_word = "你的电脑CPU型号是：AMD Ryzen 7 7840HS，性能非常强悍。"
    speak_text(test_word)
    
    import time
    time.sleep(5) # 等她念完
    print("测试完成。")