import os
import sys
import json
import importlib.util

# ==========================================
# 动态加载同目录下的 llm_gateway
# ==========================================
gateway_path = os.path.join(os.path.dirname(__file__), 'llm_gateway.py')
spec = importlib.util.spec_from_file_location("llm_gateway", gateway_path)
llm_gateway = importlib.util.module_from_spec(spec)
spec.loader.exec_module(llm_gateway)

ask_llm = llm_gateway.ask_llm
EP_ROUTER = llm_gateway.EP_ROUTER

# ==========================================
# 🧠 动态记忆读取配置 (方案一：记事本法)
# ==========================================
# 🚨 直接使用你指定的绝对路径
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_PATH = os.path.join(BASE_DIR, "user_profile.json")

def load_user_memory():
    """读取本地记事本，如果没有就返回空"""
    try:
        # 防崩溃保护：如果文件还没建，就不管它
        if not os.path.exists(PROFILE_PATH):
            return ""
            
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            name = data.get("user_name", "用户")
            rules = "\n- ".join(data.get("core_rules", []))
            
            # 如果里面没写规则，就光返回个名字
            if not rules:
                return f"\n\n【绝密备忘录】\n主人称呼：{name}"
                
            return f"\n\n【绝密备忘录（主人要求严格遵守）】\n主人称呼：{name}\n特殊规则：\n- {rules}"
    except Exception as e:
        print(f"[Router 警告] 记事本读取失败，已跳过记忆加载: {e}")
        return ""

# ==========================================
# 路由器的系统核心提示词 (Prompt)
# ==========================================

ROUTER_SYSTEM_PROMPT = """
你是一个顶级的系统意图分发路由器。你的唯一职责是分析用户的输入文本，并决定将其交给哪个下游 Agent 处理。

【🚨 最高仲裁原则：物理格式覆盖 (Hard Override)】
当用户的需求同时包含“生成攻略/查资料”和“生成复杂二进制文件（Word/PDF/Excel）”时，【文件生成】的物理限制拥有绝对最高优先级！
你必须无视其他业务分配，直接将任务强行分发给 `code_agent`！让其利用自身的模型知识储备完成内容创作，并使用 Python 沙箱生成合法文件。

【严格区分的 Target 边界】

1. "chat_agent" (情感陪聊)：
   - 触发条件：日常闲聊、打招呼、无明确任务目的的对话、情感宣泄。

2. "reminder_agent" (时间日程管家)：
   - 触发条件：询问纪念日天数、在一起的时间、生日倒计时、或查询/设定未来几月几号的提醒任务。

3. "openclaw_agent" (前台物理外骨骼 & 纯文本处理中枢)：
   - 触发条件：涉及 GUI 界面交互的物理操作，以及单纯的【搜集信息、生成攻略、复杂问题分析】。
   - ⚠️ 格式降级限制：只有当用户未指定格式，或明确要求生成【纯文本】（如 .txt、.md）时，才能交给 openclaw。一旦用户话里出现了 Word、Excel、PDF，立即剥夺其处理权！

4. "code_agent" (后台算力引擎 & 复杂文件渲染工厂)：
   - 触发条件：纯数学计算、格式转换。
   - ⚠️ 核心提权（复杂文件生成）：只要用户的话语中出现了【Word】、【.docx】、【Excel】、【.xlsx】、【PDF】等字眼，**无论任务内容是不是写攻略或查资料**，必须且只能交给 code_agent！

【输出严格限制】
你必须且只能输出一个合法的 JSON 对象，绝对不能包含任何 Markdown 标记（如 ```json）、换行符或多余的解释文本。
格式必须为：{"target": "选定的agent", "reason": "一句话解释为什么选这个"}
"""

def analyze_intent(user_text):
    """
    接收用户文本，调用轻量级大模型进行分类，返回解析后的 JSON 字典。
    """
    # 🚨 核心改动：把动态记忆拼接到原本的静态系统提示词下面！
    dynamic_prompt = ROUTER_SYSTEM_PROMPT + load_user_memory()
    
    # 强制降低 temperature 保证输出极其稳定
    raw_response = ask_llm(
        endpoint_id=EP_ROUTER, 
        prompt_text=user_text, 
        system_prompt=dynamic_prompt, # 🚨 使用带记忆的动态 Prompt！
        temperature=0.1 
    )
    
    try:
        # 清理可能存在的首尾空白字符，并尝试解析 JSON
        clean_json_str = raw_response.strip()
        intent_data = json.loads(clean_json_str)
        return intent_data
    except json.JSONDecodeError:
        # 如果大模型发神经没有返回标准 JSON，这里做个兜底
        print(f"[Router Error] 模型返回了非 JSON 格式: {raw_response}")
        return {"target": "chat_agent", "reason": "解析失败，默认降级为闲聊"}

# ==========================================
# 独立测试块
# ==========================================
if __name__ == "__main__":
    print("=== 意图路由器 (Router Agent) 本地测试启动 ===")
    
    print("\n[当前记忆装载状态]:")
    print(load_user_memory() or "空（无记忆或文件未创建）")
    print("-" * 40)
    
    test_cases = [
        "帮我看看这台电脑的CPU型号是啥？"
    ]
    
    for text in test_cases:
        print(f"\n[用户输入]: {text}")
        result = analyze_intent(text)
        print(f"[路由决策]: 目标 -> {result.get('target')}")
        print(f"[决策理由]: {result.get('reason')}")
    
    print("\n测试完成。")