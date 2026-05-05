# Sentinel-MultiAgent-Arm---
A physical desktop robot powered by Multi-Agent LLMs and a local Python sandbox. | 基于多智能体与本地沙箱的实体化桌面机甲

# PROJECT: SENTINEL (哨兵)

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

### 🌟 Project Overview
**Sentinel** is a multi-agent AI-powered desktop robot designed to bridge the gap between virtual LLMs and the physical world. Unlike traditional chatbots, Sentinel possesses a "physical body" (a robotic arm) and a "local nervous system" (Python sandbox) to execute tasks in the real world.

### 🚀 Key Features
- **Physical Interaction**: Expresses emotions and status via hardware actions (Nod, Shake, Extend, Retract).
- **Multi-Agent Brain**: Built with a custom Router Agent that dispatches tasks to specialized workers (Chat, Code, OpenClaw, Reminder).
- **Code Sandbox (The 'Magistrate')**: Executes Python code locally to generate real files (Word, Excel, Data Plots) or perform system-level tasks.
- **Event Awareness**: 
  - **QQ Radar**: Real-time message push from mobile to desktop via NapCatQQ.
  - **Black Box**: Monitors system errors and provides physical alerts when code crashes.
  - **Touch Sense**: Physical screen touch to interrupt or wake the system.
- **Voice Intelligence**: Real-time speech-to-text (ASR) via Aliyun Paraformer with X-ray vision (live subtitles on screen).

### 🛠️ Tech Stack
- **Software**: Python 3.10+, LangChain, Dashscope (Aliyun), NapCatQQ (OneBot11).
- **Hardware**: ESP32-S3, TFT LCD (ST7796), FT6336U Touch, 4x MG90S Servos.
- **Framework**: Multi-Agent Dispatcher + Local Execution Sandbox.

---

<a name="chinese"></a>
## 中文

### 🌟 项目简介
**哨兵 (Sentinel)** 是一个基于多智能体 (Multi-Agent) 架构的实体化桌面机器人。它旨在打破大模型与物理世界的隔阂，通过“躯体”（机械臂）与“本地神经”（Python 沙箱）实现真正的物理交互与任务执行。

### 🚀 核心功能
- **物理反馈交互**：通过硬件动作（点头、摇头、弹出、收回）表达情绪与系统状态。
- **多智能体大脑**：自研 Router Agent，根据意图自动分发至：情感陪聊、代码执行、物理外挂 (OpenClaw) 或日程管家。
- **代码沙箱（工部尚书）**：拒绝幻觉！在本地安全沙箱运行 Python 脚本，生成真实的物理文件（Word/Excel/图表）或执行系统级操作。
- **全局事件感知**：
  - **QQ 雷达**：基于 NapCatQQ 实现手机通知毫秒级同步至桌面。
  - **崩溃黑匣子**：全天候监控系统报错，代码崩溃时机器人会物理报警。
  - **物理触控**：支持通过触摸 ESP32 屏幕进行交互打断或强制唤醒。
- **语音语义理解**：接入阿里云 Paraformer 实时语音流，支持流式字幕展示。

### 🛠️ 技术架构
- **软件层**: Python 3.10+, LangChain, Dashscope (阿里云), NapCatQQ (OneBot11).
- **硬件层**: ESP32-S3, TFT 屏幕, 电容触摸, 4 自由度舵机机械臂。

---

## 📂 Project Structure (项目目录树)

```text
SENTINEL/
├── 1_Event_Listeners/          # 事件监听层 (感官)
│   ├── log_watcher.py          # 日志监控 (黑匣子)
│   ├── qq_receiver.py          # QQ 消息接收雷达
│   └── voice_listener.py       # 语音识别与触摸唤醒
├── 2_Brain_Core/               # 大脑核心层 (逻辑)
│   ├── llm_gateway.py          # 大模型统一网关
│   ├── router_agent.py         # 意图分发路由器
│   └── Agent_Workers/          # 专项执行特工
│       ├── chat_agent.py       # 情感陪聊
│       ├── code_agent.py       # 代码沙箱逻辑
│       ├── openclaw_agent.py   # 物理外挂适配
│       └── reminder_agent.py   # 日程管家
├── 3_Action_Executors/         # 动作执行层 (神经)
│   ├── code_env_runner.py      # Python 本地沙箱环境
│   ├── openclaw_driver.py      # OpenClaw 底层驱动
│   └── voice_speaker.py        # TTS 发声器官
├── 4_Hardware_Link/            # 硬件链路层 (骨骼)
│   └── serial_sender.py        # 串口通讯协议
├── ESP32_Firmware/             # 嵌入式固件
│   └── ESP32_Firmware.ino      # ESP32 驱动代码
├── main_controller.py          # 系统主程序入口
├── user_profile.json           # 个人记忆数据 (需自行创建)
└── reminders.json              # 日程提醒数据 (需自行创建)


📜 License & Credits (开源声明)
Software (软件)
The software core of this project is licensed under the MIT License.
本项目软件核心部分采用 MIT 开源协议。

Hardware (硬件)
The mechanical structure of the robot arm is based on "Compact Robot Arm (Arduino) - 3D Printed" by BuildSomeStuff.

Hardware License: CC BY-NC-ND (Attribution-NonCommercial-NoDerivs).

Important: This hardware is for personal non-commercial use only. Production or sale of this hardware is strictly prohibited.

硬件结构基于 BuildSomeStuff 的开源项目。遵循 CC BY-NC-ND 协议，仅限个人非商业使用，严禁量产或售卖。

Created with ❤️ by mook tetove
"""

with open("README.md", "w", encoding="utf-8") as f:
f.write(content)

```python?code_reference&code_event_index=6
with open("README.md", "w", encoding="utf-8") as f:
    f.write("# PROJECT: SENTINEL (哨兵)\n\n")
    f.write("[English](#english) | [中文](#chinese)\n\n---\n\n")
    
    # English Section
    f.write("<a name=\"english\"></a>\n## English\n\n")
    f.write("### 🌟 Project Overview\n")
    f.write("**Sentinel** is a multi-agent AI-powered desktop robot designed to bridge the gap between virtual LLMs and the physical world. Unlike traditional chatbots, Sentinel possesses a \"physical body\" (a robotic arm) and a \"local nervous system\" (Python sandbox) to execute tasks in the real world.\n\n")
    f.write("### 🚀 Key Features\n")
    f.write("- **Physical Interaction**: Expresses emotions and status via hardware actions (Nod, Shake, Extend, Retract).\n")
    f.write("- **Multi-Agent Brain**: Built with a custom Router Agent that dispatches tasks to specialized workers (Chat, Code, OpenClaw, Reminder).\n")
    f.write("- **Code Sandbox (The 'Magistrate')**: Executes Python code locally to generate real files (Word, Excel, Data Plots) or perform system-level tasks.\n")
    f.write("- **Event Awareness**: \n")
    f.write("  - **QQ Radar**: Real-time message push from mobile to desktop via NapCatQQ.\n")
    f.write("  - **Black Box**: Monitors system errors and provides physical alerts when code crashes.\n")
    f.write("  - **Touch Sense**: Physical screen touch to interrupt or wake the system.\n")
    f.write("- **Voice Intelligence**: Real-time speech-to-text (ASR) via Aliyun Paraformer with X-ray vision (live subtitles on screen).\n\n")
    
    # Chinese Section
    f.write("---\n\n<a name=\"chinese\"></a>\n## 中文\n\n")
    f.write("### 🌟 项目简介\n")
    f.write("**哨兵 (Sentinel)** 是一个基于多智能体 (Multi-Agent) 架构的实体化桌面机器人。它旨在打破大模型与物理世界的隔阂，通过“躯体”（机械臂）与“本地神经”（Python 沙箱）实现真正的物理交互与任务执行。\n\n")
    f.write("### 🚀 核心功能\n")
    f.write("- **物理反馈交互**：通过硬件动作（点头、摇头、弹出、收回）表达情绪与系统状态。\n")
    f.write("- **多智能体大脑**：自研 Router Agent，根据意图自动分发至：情感陪聊、代码执行、物理外挂 (OpenClaw) 或日程管家。\n")
    f.write("- **代码沙箱（工部尚书）**：拒绝幻觉！在本地安全沙箱运行 Python 脚本，生成真实的物理文件（Word/Excel/图表）或执行系统级操作。\n")
    f.write("- **全局事件感知**：\n")
    f.write("  - **QQ 雷达**：基于 NapCatQQ 实现手机通知毫秒级同步至桌面。\n")
    f.write("  - **崩溃黑匣子**：全天候监控系统报错，代码崩溃时机器人会物理报警。\n")
    f.write("  - **物理触控**：支持通过触摸 ESP32 屏幕进行交互打断或强制唤醒。\n")
    f.write("- **语音语义理解**：接入阿里云 Paraformer 实时语音流，支持流式字幕展示。\n\n")
    
    # Tree Structure
    f.write("---\n\n## 📂 Project Structure (项目目录树)\n\n```text\n")
    f.write("SENTINEL/\n")
    f.write("├── 1_Event_Listeners/          # 事件监听层 (感官)\n")
    f.write("│   ├── log_watcher.py          # 日志监控 (黑匣子)\n")
    f.write("│   ├── qq_receiver.py          # QQ 消息接收雷达\n")
    f.write("│   └── voice_listener.py       # 语音识别与触摸唤醒\n")
    f.write("├── 2_Brain_Core/               # 大脑核心层 (逻辑)\n")
    f.write("│   ├── llm_gateway.py          # 大模型统一网关\n")
    f.write("│   ├── router_agent.py         # 意图分发路由器\n")
    f.write("│   └── Agent_Workers/          # 专项执行特工\n")
    f.write("│       ├── chat_agent.py       # 情感陪聊\n")
    f.write("│       ├── code_agent.py       # 代码沙箱逻辑\n")
    f.write("│       ├── openclaw_agent.py   # 物理外挂适配\n")
    f.write("│       └── reminder_agent.py   # 日程管家\n")
    f.write("├── 3_Action_Executors/         # 动作执行层 (神经)\n")
    f.write("│   ├── code_env_runner.py      # Python 本地沙箱环境\n")
    f.write("│   ├── openclaw_driver.py      # OpenClaw 底层驱动\n")
    f.write("│   └── voice_speaker.py        # TTS 发声器官\n")
    f.write("├── 4_Hardware_Link/            # 硬件链路层 (骨骼)\n")
    f.write("│   └── serial_sender.py        # 串口通讯协议\n")
    f.write("├── ESP32_Firmware/             # 嵌入式固件\n")
    f.write("│   └── ESP32_Firmware.ino      # ESP32 驱动代码\n")
    f.write("├── main_controller.py          # 系统主程序入口\n")
    f.write("├── user_profile.json           # 个人记忆数据 (需自行创建)\n")
    f.write("└── reminders.json              # 日程提醒数据 (需自行创建)\n")
    f.write("```\n\n")

    # License
    f.write("---\n\n## 📜 License & Credits (开源声明)\n\n")
    f.write("### Software (软件)\n")
    f.write("The software core of this project is licensed under the **MIT License**.\n")
    f.write("本项目软件核心部分采用 **MIT 开源协议**。\n\n")
    f.write("### Hardware (硬件)\n")
    f.write("- The mechanical structure of the robot arm is based on **\"Compact Robot Arm (Arduino) - 3D Printed\"** by **BuildSomeStuff**.\n")
    f.write("- Hardware License: **CC BY-NC-ND** (Attribution-NonCommercial-NoDerivs).\n")
    f.write("- **Important**: This hardware is for personal non-commercial use only. Production or sale of this hardware is strictly prohibited.\n")
    f.write("- 硬件结构基于 BuildSomeStuff 的开源项目。遵循 **CC BY-NC-ND** 协议，仅限个人非商业使用，**严禁量产或售卖**。\n\n")
    f.write("---\nCreated with ❤️ by **mook tetove**\n")


Your Markdown file is ready

 README 
MD

为你量身定制的 GitHub README.md 已经生成完毕！

这份 README 采用了标准的双语结构（英文在上，中文在下），不仅逼格拉满，而且完美融合了你的多智能体架构、沙箱机制以及极其重要的硬件开源声明。我还专门为你绘制了基于你项目代码的 ASCII 目录框架树。

你可以直接下载上面的文件，或者直接复制以下内容到你的 GitHub 仓库中：

Markdown
# PROJECT: SENTINEL (哨兵)

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

### 🌟 Project Overview
**Sentinel** is a multi-agent AI-powered desktop robot designed to bridge the gap between virtual LLMs and the physical world. Unlike traditional chatbots, Sentinel possesses a "physical body" (a robotic arm) and a "local nervous system" (Python sandbox) to execute tasks in the real world.

### 🚀 Key Features
- **Physical Interaction**: Expresses emotions and status via hardware actions (Nod, Shake, Extend, Retract).
- **Multi-Agent Brain**: Built with a custom Router Agent that dispatches tasks to specialized workers (Chat, Code, OpenClaw, Reminder).
- **Code Sandbox (The 'Magistrate')**: Executes Python code locally to generate real files (Word, Excel, Data Plots) or perform system-level tasks.
- **Event Awareness**: 
  - **QQ Radar**: Real-time message push from mobile to desktop via NapCatQQ.
  - **Black Box**: Monitors system errors and provides physical alerts when code crashes.
  - **Touch Sense**: Physical screen touch to interrupt or wake the system.
- **Voice Intelligence**: Real-time speech-to-text (ASR) via Aliyun Paraformer with X-ray vision (live subtitles on screen).

### 🛠️ Tech Stack
- **Software**: Python 3.10+, LangChain, Dashscope (Aliyun), NapCatQQ (OneBot11).
- **Hardware**: ESP32-S3, TFT LCD (ST7796), FT6336U Touch, 4x MG90S Servos.
- **Framework**: Multi-Agent Dispatcher + Local Execution Sandbox.

---

<a name="chinese"></a>
## 中文

### 🌟 项目简介
**哨兵 (Sentinel)** 是一个基于多智能体 (Multi-Agent) 架构的实体化桌面机器人。它旨在打破大模型与物理世界的隔阂，通过“躯体”（机械臂）与“本地神经”（Python 沙箱）实现真正的物理交互与任务执行。

### 🚀 核心功能
- **物理反馈交互**：通过硬件动作（点头、摇头、弹出、收回）表达情绪与系统状态。
- **多智能体大脑**：自研 Router Agent，根据意图自动分发至：情感陪聊、代码执行、物理外挂 (OpenClaw) 或日程管家。
- **代码沙箱（工部尚书）**：拒绝幻觉！在本地安全沙箱运行 Python 脚本，生成真实的物理文件（Word/Excel/图表）或执行系统级操作。
- **全局事件感知**：
  - **QQ 雷达**：基于 NapCatQQ 实现手机通知毫秒级同步至桌面。
  - **崩溃黑匣子**：全天候监控系统报错，代码崩溃时机器人会物理报警。
  - **物理触控**：支持通过触摸 ESP32 屏幕进行交互打断或强制唤醒。
- **语音语义理解**：接入阿里云 Paraformer 实时语音流，支持流式字幕展示。

### 🛠️ 技术架构
- **软件层**: Python 3.10+, LangChain, Dashscope (阿里云), NapCatQQ (OneBot11).
- **硬件层**: ESP32-S3, TFT 屏幕, 电容触摸, 4 自由度舵机机械臂。

---

## 📂 Project Structure (项目目录树)

```text
SENTINEL/
├── 1_Event_Listeners/          # 事件监听层 (感官)
│   ├── log_watcher.py          # 日志监控 (黑匣子)
│   ├── qq_receiver.py          # QQ 消息接收雷达
│   └── voice_listener.py       # 语音识别与触摸唤醒
├── 2_Brain_Core/               # 大脑核心层 (逻辑)
│   ├── llm_gateway.py          # 大模型统一网关
│   ├── router_agent.py         # 意图分发路由器
│   └── Agent_Workers/          # 专项执行特工
│       ├── chat_agent.py       # 情感陪聊
│       ├── code_agent.py       # 代码沙箱逻辑
│       ├── openclaw_agent.py   # 物理外挂适配
│       └── reminder_agent.py   # 日程管家
├── 3_Action_Executors/         # 动作执行层 (神经)
│   ├── code_env_runner.py      # Python 本地沙箱环境
│   ├── openclaw_driver.py      # OpenClaw 底层驱动
│   └── voice_speaker.py        # TTS 发声器官
├── 4_Hardware_Link/            # 硬件链路层 (骨骼)
│   └── serial_sender.py        # 串口通讯协议
├── ESP32_Firmware/             # 嵌入式固件
│   └── ESP32_Firmware.ino      # ESP32 驱动代码
├── main_controller.py          # 系统主程序入口
├── user_profile.json           # 个人记忆数据 (需自行创建)
└── reminders.json              # 日程提醒数据 (需自行创建)

----------------------------------------------------------------------------
📜 License & Credits (开源声明)
Software (软件)
The software core of this project is licensed under the MIT License.
本项目软件核心部分采用 MIT 开源协议。

Hardware (硬件)
The mechanical structure of the robot arm is based on "Compact Robot Arm (Arduino) - 3D Printed" by BuildSomeStuff.
Hardware License: CC BY-NC-ND (Attribution-NonCommercial-NoDerivs).
Important: This hardware is for personal non-commercial use only. Production or sale of this hardware is strictly prohibited.
硬件结构基于 BuildSomeStuff 的开源项目。遵循 CC BY-NC-ND 协议，仅限个人非商业使用，严禁量产或售卖。
Created with ❤️ by mook tetove
