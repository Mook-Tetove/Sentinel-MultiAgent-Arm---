import os
import importlib.util

# ==========================================
# 动态加载兄弟目录的 Driver (因为文件夹带数字，必须这样写)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))          # Agent_Workers 目录
pc_server_dir = os.path.dirname(os.path.dirname(current_dir))     # PC_Server 根目录
driver_path = os.path.join(pc_server_dir, "3_Action_Executors", "openclaw_driver.py")

spec = importlib.util.spec_from_file_location("openclaw_driver", driver_path)
openclaw_driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openclaw_driver)
# ==========================================

def handle_openclaw_task(user_text):
    print(f"\n[物理外挂] 脑区已收到指令，正在呼叫底层神经驱动...")
    
    # 1. 呼叫特种兵(Driver)去干活，脑区就在这等着
    result = openclaw_driver.execute_cli_command(user_text)
    
    # 2. 根据特种兵带回来的情报，进行“语言包装”
    if result["status"] == "timeout":
        return "<action: nod_head> 任务太复杂了，它还在后台跑，我就先不干等了。"
        
    elif result["status"] in ["error", "exception"]:
        error_info = result["stderr"][-50:] # 取最后50个字符防止太长念不完
        print(f"   [底层报错] ->\n{result['stderr']}")
        return f"<action: shake_head> 神经通路受阻，底层反馈说：{error_info}"
        
    elif result["status"] == "success":
        # 成功了！开始“抠”出大模型说的人话
        output = result["stdout"]
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        
        # 过滤掉以 '[' 开头的系统日志（比如 [plugins] ...）
        clean_lines = [line for line in lines if not line.startswith('[')]
        
        if clean_lines:
            # 拿最后一行（通常是结语）
            final_reply = clean_lines[-1]
            return f"<action: nod_head> {final_reply}"
        else:
            return "<action: nod_head> 任务已完成，但大模型这次没写结语。"

if __name__ == "__main__":
    print("=== OpenClaw 物理外挂：脑区拆分闭环测试 ===")
    res = handle_openclaw_task("搜一下北京天气并用一句话总结") 
    print(f"\n最终结果: {res}")