import os
from langchain_openai import ChatOpenAI

# ==========================================
# 统一配置区：在这里填入你新申请的 Key 和 Endpoint
# ==========================================
VOLC_API_KEY = "YOUR_API_KEY_HERE"
VOLC_BASE_URL = "YOUR_BASE_URL_HERE"

# 预留三个 Endpoint ID 的常量位置
EP_ROUTER = "model name"  # 用于意图分类的轻量模型
EP_CHAT = "model name"    # 用于日常对话的模型
EP_CODE = "model name"    # 用于代码逻辑分析的推理模型

def get_llm_client(endpoint_id, temperature=0.3):
    """
    动态初始化大模型客户端。
    接收 endpoint_id 参数，实例化对应的模型。
    """
    try:
        llm = ChatOpenAI(
            model=endpoint_id,
            api_key=VOLC_API_KEY,
            base_url=VOLC_BASE_URL,
            temperature=temperature,
            max_tokens=1024
        )
        return llm
    except Exception as e:
        print(f"[Gateway Error] 客户端初始化失败: {e}")
        return None

def ask_llm(endpoint_id, prompt_text, system_prompt="你是一个有用的助手。", temperature=0.3):
    """
    提供给各个 Agent 调用的通用问答接口。
    """
    client = get_llm_client(endpoint_id, temperature)
    if not client:
        return "本地系统错误：无法构建大模型客户端。"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_text}
    ]
    
    try:
        response = client.invoke(messages)
        return response.content
    except Exception as e:
        return f"[Gateway Error] 网络请求超时或失败: {str(e)}"

# ==========================================
# 独立测试块
# ==========================================
if __name__ == "__main__":
    print("正在进行动态网关测试...")
    # 注意：运行测试前，请务必把上面的 VOLC_API_KEY 和 EP_ROUTER 替换为真实的字符串
    
    test_user_input = "测试动态路由接口连通性。"
    test_system_prompt = "直接回复'网关接口正常'，不要输出其他字符。"
    
    # 模拟 Router Agent 调用网关，传入 EP_ROUTER
    result = ask_llm(EP_ROUTER, test_user_input, test_system_prompt)
    print(f"\n[大模型返回结果] {result}")