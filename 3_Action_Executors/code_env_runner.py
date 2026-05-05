import os
import subprocess
import tempfile

def execute_python_code(code_string, timeout_seconds=120):
    """
    在本地安全沙箱（子进程）中执行 Python 代码。
    返回一个字典，包含执行状态、标准输出和错误输出。
    """
    # 1. 创建一个安全的临时文件，用完即焚
    fd, temp_path = tempfile.mkstemp(suffix=".py", text=True)
    
    try:
        # 将大模型生成的代码写入临时文件
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(code_string)
        
# 2. 启动子进程执行这个临时文件
        # 加入 "-X", "utf8" 强制 Windows 的 Python 子进程使用纯正的 UTF-8 输出
        result = subprocess.run(
            ["python", "-X", "utf8", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            encoding='utf-8',
            errors='replace'  # 加上容错机制，遇到奇葩字符自动替换而不是直接崩溃
        )
        
        # 3. 解析执行结果
        if result.returncode == 0:
            return {
                "status": "success",
                "output": result.stdout.strip(),
                "error": ""
            }
        else:
            return {
                "status": "failed",
                "output": result.stdout.strip(),
                "error": result.stderr.strip()
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "output": "",
            "error": f"代码执行超时（超过 {timeout_seconds} 秒被强制终止），请检查是否存在死循环。"
        }
    except Exception as e:
        return {
            "status": "system_error",
            "output": "",
            "error": str(e)
        }
    finally:
        # 4. 毁尸灭迹：无论成功还是失败，执行完必须删除临时文件
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

# ==========================================
# 独立测试块
# ==========================================
if __name__ == "__main__":
    print("=== 正在测试本地代码沙箱 (Code Env Runner) ===")
    
    # 模拟大模型写的一段成功代码
    test_code_success = """
print('Hello, 这是来自沙箱内部的声音！')
a = 10
b = 20
print(f'计算结果: a + b = {a+b}')
"""

    # 模拟大模型写的一段报错代码（故意写错除数为0）
    test_code_error = """
print('准备执行除法计算...')
result = 10 / 0
print(result)
"""

    print("\n[测试 1：正常代码执行]")
    res1 = execute_python_code(test_code_success)
    print(f"状态: {res1['status']}")
    print(f"输出:\n{res1['output']}")
    
    print("\n[测试 2：报错代码拦截]")
    res2 = execute_python_code(test_code_error)
    print(f"状态: {res2['status']}")
    print(f"正常输出: {res2['output']}")
    print(f"拦截到的红字报错:\n{res2['error']}")