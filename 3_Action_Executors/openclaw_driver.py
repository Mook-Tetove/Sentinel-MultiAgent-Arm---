import subprocess
import threading
import queue
import time
import re

def strip_ansi(text):
    """卸妆水：专门扒掉控制台输出的隐藏颜色代码和转义字符"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def is_junk_log(line):
    """垃圾桶：只要包含这些词，不管它长啥样，统统扔掉"""
    junk_words = ['Gateway', 'Source', 'Config', 'Bind', '[plugins]', 'Registered', 'feishu_', 'openclaw-']
    return any(word in line for word in junk_words)

def execute_cli_command(user_text):
    """终极清道夫驱动：防卡死 + 强力卸妆"""
    
    # 🧠 加强版思想钢印
    magic_prompt = (
        f"{user_text} "
        f"【系统级强制指令：1. 如果要打开或运行程序，必须使用 'start 程序名'，绝不准直接运行！"
        f"2. 执行成功后，必须用一句简短的中文向我汇报（例如：'记事本已打开'）。】"
    )
    cmd = f'openclaw agent --agent main --message "{magic_prompt}"'
    
    process = subprocess.Popen(
        cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True, 
        encoding='utf-8',
        errors='replace'
    )
    
    q = queue.Queue()
    
    def reader():
        for line in iter(process.stdout.readline, ''):
            q.put(line)
        process.stdout.close()
        
    threading.Thread(target=reader, daemon=True).start()
    
    output_lines = []
    last_read_time = time.time()
    SILENCE_TIMEOUT = 3.0  
    ABSOLUTE_TIMEOUT = 300.0 
    
    while True:
        try:
            line = q.get(timeout=0.5)
            # 核心操作：拿到字的第一时间，先泼卸妆水！
            clean_line = strip_ansi(line).strip()
            
            if clean_line:
                output_lines.append(clean_line)
                last_read_time = time.time() 
                
        except queue.Empty:
            if process.poll() is not None:
                break 
            
            if time.time() - last_read_time > SILENCE_TIMEOUT and len(output_lines) > 0:
                # 检查有没有说过人话（不是垃圾日志）
                if any(not is_junk_log(l) for l in output_lines):
                    process.terminate()
                    process.kill()
                    break
                    
            if time.time() - last_read_time > ABSOLUTE_TIMEOUT:
                process.kill()
                return {"status": "timeout", "stderr": "绝对超时"}

    # ==========================================
    # 终极过滤：只提取大模型说的“人话”
    # ==========================================
    human_lines = [l for l in output_lines if not is_junk_log(l)]
    
    if human_lines:
        return {"status": "success", "stdout": human_lines[-1], "stderr": ""}
    else:
        return {"status": "success", "stdout": "操作已在后台执行完毕。", "stderr": ""}

if __name__ == "__main__":
    print("=== 底层驱动 终极防卡死+卸妆 版 测试 ===")
    res = execute_cli_command("打开记事本")
    print(f"\n提取结果: {res}")