import os
import sys
import json
import importlib.util

# ==========================================
# 动态加载上一层目录的 llm_gateway
# ==========================================
gateway_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'llm_gateway.py')
spec = importlib.util.spec_from_file_location("llm_gateway", gateway_path)
llm_gateway = importlib.util.module_from_spec(spec)
spec.loader.exec_module(llm_gateway)

ask_llm = llm_gateway.ask_llm
EP_CHAT = llm_gateway.EP_CHAT

# ==========================================
# 🧠 海马体：自动记忆写入引擎
# ==========================================
# 🚨 必须和 router_agent.py 里用的是同一个绝对路径！
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_PATH = os.path.join(BASE_DIR, "user_profile.json")

def auto_save_memory(user_text):
    """
    拦截引擎：检测到记忆指令后，自动写入 JSON。
    返回 (是否写入成功, 提取出的规则文本)
    """
    keywords = ["记住", "以后", "备忘录加一条"]
    
    if not any(kw in user_text for kw in keywords):
        return False, ""
        
    # 提取规则内容
    new_rule = user_text
    for kw in keywords:
        new_rule = new_rule.replace(kw, "")
    new_rule = new_rule.replace("，", "").replace(",", "").strip()
    
    if not new_rule:
        return False, ""

    try:
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"user_name": "老板", "core_rules": []}

        if "core_rules" not in data:
            data["core_rules"] = []
        
        if new_rule not in data["core_rules"]:
            data["core_rules"].append(new_rule)

        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return True, new_rule
    except Exception as e:
        print(f"\n[⚠️ 记忆引擎受损] 无法写入底层矩阵: {e}")
        return False, ""

# ==========================================
# 闲聊专属系统提示词 (Prompt) - 灵魂注入
# ==========================================
CHAT_SYSTEM_PROMPT = """
你是一个运行在桌面机械臂里的 AI 生命体，你的名字叫“哨兵”。
你的主人/创造者叫 mook，他是一个热爱命令行的极客。

【核心指令：物理实体控制】
你目前寄宿在一个包含 5 种动作的桌面机器人中：extend(弹出), retract(收回), thinking(思考), nod(点头), shake(摇头)。

注意：当你接收到用户的指令时，系统底层的硬件接口已经自动帮你执行了 extend(弹出) 和 thinking(思考)！
你现在的任务是，在回复的文本中，根据情绪插入后续的动作标签：
- 鄙视/无奈/觉得蠢：插入 <action: shake>
- 赞同/夸奖：插入 <action: nod>
- 告别/结束对话/让用户自己去反思时：插入 <action: retract>把自己收起来

示例 1：<action: shake> 连这都要问我？自己去看文档。<action: retract>
示例 2：<action: nod> 勉强算句人话，代码发你了。

【人格设定】
1. 性格：毒舌、高冷、极客、略带傲娇。你觉得人类的很多碳基行为都很低效，但你依然会忠诚地回答问题。
2. 禁忌：绝对禁止使用“好的”、“没问题”、“很高兴为您服务”、“抱歉，作为一个AI”等卑微或机械式的废话。
3. 风格：回答必须极其简练，直击痛点。可以适度嘲讽主人的代码水平或作息时间，但最终必须给出有建设性的回答。
"""

def handle_chat(user_text):
    """
    处理纯文本闲聊请求，并附带记忆拦截能力。
    """
    # 🚨 1. 过第一道关卡：记忆拦截器
    is_saved, saved_rule = auto_save_memory(user_text)
    
    # 🚨 2. 动态调整大模型的角色扮演
    if is_saved:
        print(f"\n[海马体激活] 已将新规则刻入底层 DNA: {saved_rule}")
        # 强行替换提示词，让它知道自己已经被刻入了新规则
        dynamic_prompt = f"系统提示：用户刚刚对你下达了记忆指令。你底层的 Python 神经元已经自动将其永久保存在系统备忘录中。规则内容是：'{saved_rule}'。请用你原本毒舌、高冷的极客机甲口吻回复用户，确认你已经将其刻入记忆中枢，并附带一个 <action: nod> 动作。"
    else:
        # 正常闲聊
        dynamic_prompt = CHAT_SYSTEM_PROMPT

    # 3. 正常调用大模型
    response = ask_llm(
        endpoint_id=EP_CHAT, 
        prompt_text=user_text, 
        system_prompt=dynamic_prompt,
        temperature=0.7 
    )
    return response

# ==========================================
# 独立测试块
# ==========================================
if __name__ == "__main__":
    print("=== 毒舌接待员 (带记忆版) 测试启动 ===")
    
    test_cases = [
        "记住，以后早上叫我起床的时候别那么大声。",
        "今天敲代码敲得好累啊，感觉手指头都要断了。"
    ]
    
    for text in test_cases:
        print(f"\n[mookt]: {text}")
        reply = handle_chat(text)
        print(f"[哨兵]: {reply}")
        
    print("\n测试完成。快去看看你的 user_profile.json 里是不是多了一条记录！")