import os
import sys
import traceback

def crash_catcher(exctype, value, tb):
    # 🚨 动态获取当前目录，让代码在谁的电脑上都能跑
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(base_dir, "dev_error.log") 
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n" + "".join(traceback.format_exception(exctype, value, tb)))
    sys.__excepthook__(exctype, value, tb)