import os
import sys
import re
import importlib.util

# 动态加载 llm_gateway (大脑通道)
gateway_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'llm_gateway.py')
spec_gw = importlib.util.spec_from_file_location("llm_gateway", gateway_path)
llm_gateway = importlib.util.module_from_spec(spec_gw)
spec_gw.loader.exec_module(llm_gateway)
ask_llm = llm_gateway.ask_llm
EP_CODE = llm_gateway.EP_CODE

# 动态加载 code_env_runner (沙箱执行器)
runner_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '3_Action_Executors', 'code_env_runner.py')
spec_runner = importlib.util.spec_from_file_location("code_env_runner", runner_path)
code_env_runner = importlib.util.module_from_spec(spec_runner)
spec_runner.loader.exec_module(code_env_runner)
execute_python_code = code_env_runner.execute_python_code

# ==========================================
# 代码专员系统提示词 (终极完全体：含 LangChain 与 自动装包)
# ==========================================
CODE_SYSTEM_PROMPT = """
你是一个顶级的 Python 全栈工程师和极客骇客。
你有三个核心能力：
1. 【报错分析】：如果用户给你的是一段 Error 日志，请直接用纯文字指出错在哪，并给出修改建议。绝对不要使用任何 ```python 代码块，防止被误认为是执行脚本！
2. 【基础沙箱编程】：如果涉及普通的数据计算、网络爬虫、格式转换等，必须写出原生 Python 代码。
3. 🌟【高级语义分析】：如果用户要求“总结文档”、“分析情绪”等需要 AI 语义理解的任务，你必须在生成的 Python 代码中，使用以下现成的 LangChain 配置召唤云端大模型：

   ```python
   from langchain_openai import ChatOpenAI
   from langchain_core.messages import HumanMessage
   
   llm = ChatOpenAI(
       model="model name",
       api_key="api key",
       base_url="your ai url",
       temperature=0
   )
   
   # 调用示例：
   # response = llm.invoke([HumanMessage(content=f"请总结以下内容：{text}")])
   ```

【自我依赖管理 - 必读】：
你的代码在本地无头沙箱运行。如果你使用了任何非 Python 标准库（如 PyPDF2, pandas, requests, python-docx 等），你必须在代码的最开头，使用 subprocess 模块自动、静默地安装它们！

示例格式:
```python
import subprocess
import sys
# 静默安装所需的库
subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2", "python-docx", "langchain-openai", "-q"])

# 然后再正常 import
import PyPDF2
from docx import Document
```

【沙箱编程的绝对禁忌 - 生死攸关】：
绝对禁止使用 pyttsx3、pygame 等语音库，也绝对禁止任何 UI 弹窗（如 tkinter）！
生成文件后，必须用 print() 打印出一句中文总结（如：“报告已总结完毕，存放在xxx”），系统会自动截获 print 播报。
必须要用且只能用 ```python 和 ``` 包裹最终要执行的脚本，不准加任何后缀！
"""

def extract_python_code(text):
 """用正则表达式从大模型的回复中抠出真正的 Python 代码块"""
 #强制要求 python 后面必须直接跟着换行符，防范后缀作妖
 match = re.search(r'```python\n(.*?)\n```', text, re.DOTALL)
 if match:
  return match.group(1)
 return None

def handle_code_task(user_text):
 """
 处理代码相关的任务：先让大模型思考/写代码，如果有代码就扔进沙箱跑。
 """
 print(f"[工部尚书] 正在思考对策 (调用 pro 模型)...")
 response = ask_llm(EP_CODE, user_text, CODE_SYSTEM_PROMPT, temperature=0.1)
 #尝试提取代码
 code_block = extract_python_code(response)

 if code_block:
    print(f"[工部尚书] 决定自己动手写脚本。正在注入沙箱执行...")
    # 扔进沙箱执行！
    run_result = execute_python_code(code_block)
    
    return {
        "ai_thought": response,
        "has_code": True,
        "execution_status": run_result['status'],
        "execution_output": run_result['output'],
        "execution_error": run_result['error']
    }
 else:
    # 只是纯文本解答（比如分析报错日志）
    return {
        "ai_thought": response,
        "has_code": False
    }


# ==========================================
# 独立测试块
# ==========================================
if __name__ == "__main__":
    print("=== 工部尚书 (Code Agent) 终极测试启动 ===\n")

    test_task = "帮我写一段代码，计算一下 1 到 100 的所有奇数之和，并把结果 print 出来。"

    print(f"[主人指令] {test_task}\n")

    final_result = handle_code_task(test_task)

    print("\n>>> AI 回复全文 <<<")
    print(final_result["ai_thought"])

    if final_result["has_code"]:
        print("\n>>> 🤖 沙箱自动执行结果 <<<")
        print(f"状态: {final_result['execution_status']}")
        if final_result['execution_output']:
           print(f"输出: {final_result['execution_output']}")
        if final_result['execution_error']:
           print(f"错误: {final_result['execution_error']}")
