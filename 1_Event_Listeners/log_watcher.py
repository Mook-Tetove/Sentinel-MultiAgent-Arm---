import time
import os

def watch_logs(log_file_path, callback):
    """
    工业级千里眼：带防抖、冷却、截断机制的真实日志监控
    """
    print(f"👀 千里眼已开启，正在死盯真实开发日志: {log_file_path}")
    
    # 确保文件存在，没有就建一个空的
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write("")

    # 获取初始文件大小，从文件末尾开始监控，忽略以前的旧报错
    current_size = os.path.getsize(log_file_path)
    
    # 核心参数配置
    ERROR_KEYWORDS = ['Traceback (most recent call last):', 'Exception:', 'Error:']
    COOLDOWN_SECONDS = 15  # 报警冷却时间：15秒内绝不重复报警
    last_alarm_time = 0

    while True:
        try:
            time.sleep(1) # 每秒巡视一次
            
            new_size = os.path.getsize(log_file_path)
            if new_size == current_size:
                continue # 文件没变，继续睡
                
            if new_size < current_size:
                # 文件被清空了（比如你重新运行了程序）
                current_size = new_size
                continue

            # 文件变大了！有人写入了新东西！
            with open(log_file_path, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(current_size)
                new_text = f.read()
                current_size = new_size
                
                # 检查是否包含致命报错关键词
                if any(keyword in new_text for keyword in ERROR_KEYWORDS):
                    
                    # 1. 检查冷却时间
                    if time.time() - last_alarm_time < COOLDOWN_SECONDS:
                        print(f"👀 [千里眼]: 发现报错，但在冷却期内，忽略本次物理报警。")
                        continue
                    
                    # 2. 防抖机制：等报错全打印完
                    print(f"👀 [千里眼]: 察觉到异常波动，正在等待报错喷吐完毕...")
                    time.sleep(2) # 等2秒，让几十行堆栈全部写进文件
                    
                    # 重新读取这2秒内新增的所有内容
                    new_size = os.path.getsize(log_file_path)
                    with open(log_file_path, 'r', encoding='utf-8', errors='replace') as f2:
                        # 读取最近的文本（不一定要从头读，读最后一部分即可）
                        f2.seek(max(0, new_size - 5000)) 
                        full_error_text = f2.read()
                        current_size = new_size
                    
                    # 3. 智能截断：只取最后 25 行发给大模型（因为真正的死因都在最后）
                    error_lines = full_error_text.strip().split('\n')
                    core_error = '\n'.join(error_lines[-25:])
                    
                    print(f"👀 [千里眼]: 捕获完整错误核心，拉响警报！")
                    last_alarm_time = time.time() # 刷新冷却计时器
                    
                    # 呼叫主控的 callback
                    callback(core_error)

        except KeyboardInterrupt:
            break
        except Exception as e:
            # 千里眼自己瞎了不报警，静默恢复
            time.sleep(2)