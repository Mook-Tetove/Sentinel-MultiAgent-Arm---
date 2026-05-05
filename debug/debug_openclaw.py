import subprocess
import sys

def run_debug_test(user_text):
    print("=======================================")
    print(f"🚀 [物理外挂透视镜] 测试指令: {user_text}")
    print("=======================================")
    
    # 加上我们之前写的思想钢印
    magic_prompt = (
        f"{user_text} "
        f"【系统级警告：如果要执行exe或打开程序，请务必使用 'start 程序名'，不要直接运行！】"
    )
    cmd = f'openclaw agent --agent main --message "{magic_prompt}"'
    
    # 核心改变：用 Popen 实时拉取日志，不傻等！
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # 把报错和正常输出揉在一起，看得更清
        text=True,
        encoding='utf-8',
        errors='replace' # 防止偶尔的乱码卡死程序
    )
    
    print("--- ⬇️ 实时底层流日志开始 ⬇️ ---")
    
    try:
        # 一行一行地把 OpenClaw 肚子里的东西往外掏
        for line in iter(process.stdout.readline, ''):
            clean_line = line.strip()
            if clean_line:
                print(f"👉 {clean_line}")
                
    except KeyboardInterrupt:
        print("\n🛑 [手动终止] 掐断进程！")
        process.kill()
        
    process.wait()
    print(f"--- ⬆️ 进程彻底死亡，退出码: {process.returncode} ⬆️ ---")

if __name__ == "__main__":
    # 我们就拿这个罪魁祸首开刀！
    run_debug_test("打开任务管理器")