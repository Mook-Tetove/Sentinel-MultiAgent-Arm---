import os
import time
import threading
import speech_recognition as sr
import dashscope
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult

# 你的阿里云 Key
dashscope.api_key = "YOUR_ALIYUN_API_KEY_HERE"

WAKE_WORDS = ["贾维斯", "启动系统", "呼叫哨兵", "哨兵"]

# ==========================================
# 🚨 跨线程物理唤醒信号兵
# ==========================================
force_record_event = threading.Event() 

def trigger_physical_wake():
    """暴露给主控的接口：摸一下屏幕，强行扭开录音开关"""
    force_record_event.set()

print("🧠 [耳朵] 正在连接阿里云 Paraformer 实时语音大模型...")

class AliyunASRCallback(RecognitionCallback):
    def __init__(self, on_realtime_text=None): # 🚨 新增：实时字幕通道
        self.text = ""
        self.is_done = False
        self.on_realtime_text = on_realtime_text

    def on_open(self) -> None: pass
    def on_close(self) -> None: self.is_done = True

    def on_event(self, result: RecognitionResult) -> None:
        sentence = result.get_sentence()
        if sentence:
            if isinstance(sentence, list) and len(sentence) > 0:
                self.text = sentence[0].get('text', '')
            elif isinstance(sentence, dict):
                self.text = sentence.get('text', '')
                
            # 🚨 核心拦截：只要有字，立刻通过通道扔出去！
            if self.on_realtime_text and self.text:
                self.on_realtime_text(self.text)

    def on_error(self, result: RecognitionResult) -> None:
        print(f"❌ [阿里云接口报错] {result.message}")
        self.is_done = True

def transcribe_audio_aliyun(audio_data, is_active=False, on_xray_callback=None):
    """【升级版】：实时字幕阀门控制"""
    
    def handle_realtime(current_text):
        # 🚨 阀门：只有在机甲抬头（唤醒）时，才把边说边识别的字推给屏幕
        if is_active and on_xray_callback:
            clean_realtime = current_text.strip("。，！？,.!? ")
            if clean_realtime:
                on_xray_callback(clean_realtime)

    callback = AliyunASRCallback(on_realtime_text=handle_realtime)
    recognition = Recognition(model='paraformer-realtime-v1', format='pcm', sample_rate=16000, callback=callback)
    
    try:
        recognition.start()
        raw_data = audio_data.get_raw_data() 
        chunk_size = 3200 
        
        for i in range(0, len(raw_data), chunk_size):
            recognition.send_audio_frame(raw_data[i:i+chunk_size])
            time.sleep(0.005) 
            
        recognition.stop()
        
        timeout = 50 
        while not callback.is_done and timeout > 0:
            time.sleep(0.1)
            timeout -= 1
            
        return callback.text.strip("。，！？,.!? ")
    except Exception as e:
        print(f"❌ [阿里云连线异常] {e}")
        return ""

def start_listening(on_text_callback=None, on_xray_callback=None):
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False  
    r.energy_threshold = 300            
    r.pause_threshold = 1.5             
    r.non_speaking_duration = 0.5       
    
    try:
        mic = sr.Microphone(sample_rate=16000)
    except Exception as e:
        print(f"❌ [硬件错误] 找不到麦克风: {e}")
        return
        
    print("🎤 [耳朵] 正在校准麦克风底噪，请安静 1 秒...")
    
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)
        
        print(f"\n✅ [在线听觉已激活] 采样率 16kHz。")
        print(f"👉 语音唤醒:【贾维斯】或【哨兵】")
        print(f"⚡ 物理唤醒:【触摸屏幕】直接下达指令\n")
        
        is_active = False
        active_deadline = 0
        ACTIVE_DURATION = 8  
        
        while True:
            try:
                # =================================================
                # 🔪 神经切片 1：检查是否有物理触摸信号
                # =================================================
                if force_record_event.is_set():
                    force_record_event.clear() # 收到信号，立马复位
                    print("\n⚡ [物理触发] 屏幕被触摸，神经元已强行接管麦克风！")
                    
                    is_active = True # 进入专属聆听状态！
                    active_deadline = time.time() + ACTIVE_DURATION
                    
                    # 🚨 呼叫大脑执行“标准唤醒动作”(弹起+说我在)
                    if on_text_callback: on_text_callback("[JUST_WAKE]")
                    time.sleep(1.5) # 给机甲一点物理动作的时间
                    continue # 重新进入下面的 listen 去录音

                # =================================================
                # 🎤 神经切片 2：正常的语音唤醒词监听
                # =================================================
                if is_active and time.time() > active_deadline:
                    is_active = False
                    print("😴 [耳朵] 8秒内未收到指令，已缩回，重新进入潜伏状态...")
                
                try:
                    # 轮询极快，防止漏掉触摸动作
                    audio = r.listen(source, timeout=0.5, phrase_time_limit=5 if is_active else 10)
                except sr.WaitTimeoutError:
                    continue 
                
                text = transcribe_audio_aliyun(audio, is_active=is_active, on_xray_callback=on_xray_callback)
                
                if not text: continue
                clean_text = text.strip("。，！？,.!? ")
                if not clean_text or clean_text in ["谢谢", "谢谢观看", "请按时吃药"]:
                    continue
                    
                if not is_active:
                    print(f"☁️ [阿里云 X光] 实际听到: '{clean_text}'")

                text_lower = clean_text.lower()
                triggered_word = ""
                for word in WAKE_WORDS:
                    if word in text_lower:
                        triggered_word = word
                        break

                if triggered_word:
                    command = text_lower.split(triggered_word)[-1].strip("。，！？,.!? ")
                    if command:
                        print(f"🚀 [连读指令]: {command}")
                        is_active = False 
                        if on_text_callback: on_text_callback(command)
                    else:
                        print(f"👀 [双段唤醒] 命中 '{triggered_word}'！等待下发指令...")
                        is_active = True # 进入专属聆听状态！
                        active_deadline = time.time() + ACTIVE_DURATION
                        
                        # 🚨 呼叫大脑执行“标准唤醒动作”(弹起+说我在)
                        if on_text_callback: on_text_callback("[JUST_WAKE]")
                        time.sleep(1.5) 
                        
                elif is_active:
                    print(f"🚀 [免唤醒指令接收]: {clean_text}")
                    is_active = False 
                    if on_text_callback: on_text_callback(clean_text)
                    
            except KeyboardInterrupt:
                print("\n[耳朵] 已手动关闭。")
                break
            except Exception as e:
                print(f"\n❌ [底层监听崩溃，被当场抓获！] {e}")
                time.sleep(0.1)

if __name__ == "__main__":
    def test_cb(t): print(f"【大脑接收】: {t}")
    start_listening(on_text_callback=test_cb)