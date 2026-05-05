import sys
import traceback
import os

# ==========================================
# 🐞 模拟你在别的地方写代码时的崩溃拦截器
# ==========================================
def crash_catcher(exctype, value, tb):
    # 精准定位到哨兵正在监视的那个错误日志
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(BASE_DIR, "dev_error.log")
    
    with open(log_path, "a", encoding="utf-8") as f:
        # 把详细报错（遗言）写进哨兵的监控文件里
        f.write("\n" + "".join(traceback.format_exception(exctype, value, tb)))
    
    # 在 VS Code 的控制台里正常打印红字
    sys.__excepthook__(exctype, value, tb)

# 劫持 Python 系统的全局报错神经
sys.excepthook = crash_catcher
# ==========================================

print("💣 警告：倒计时 3 秒后，即将发生致命除零错误...")
import time
time.sleep(3)

# 制造一场极其惨烈的车祸！
print("💥 砰！")
result = 10 / 0  # ZeroDivisionError!