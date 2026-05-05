#include <TFT_eSPI.h>
#include <ArduinoJson.h> 
#include <Wire.h>
#include <FT6336U.h>
#include <U8g2_for_TFT_eSPI.h> 

TFT_eSPI tft = TFT_eSPI(); 
U8g2_for_TFT_eSPI u8f;         
FT6336U ts = FT6336U(17, 18, -1, -1); 
HardwareSerial ZlinkSerial(1); 

// 🚨 肌肉坐标
int homePos[4] =   {1600, 800, 1420, 2300};  // 收回状态 (趴下)
int extendPos[4] = {1600, 1300, 900, 1700};  // 弹出状态 (抬头)
int standbyPos[4] = {1600, 800, 1420, 1900}; //待机状态

// 👁️ 视觉神经变量 (新增)
bool isSleeping = true;
unsigned long lastBlinkTime = 0;
bool eyesOpen = true;
int nextBlinkDelay = 3000;

void setup() {
  // 🚨 增强第一步：加大串口接收缓冲区，防止长消息溢出
  Serial.setRxBufferSize(1024); 
  Serial.begin(115200);
  
  // 🚨 增强第二步：延长读取超时。长消息传输需要时间，50ms 太紧了，改到 200ms
  Serial.setTimeout(200); 

  ZlinkSerial.begin(115200, SERIAL_8N1, 16, 15);
  pinMode(4, OUTPUT); digitalWrite(4, LOW); delay(20); digitalWrite(4, HIGH); 

  tft.init(); tft.invertDisplay(true); tft.setRotation(1); tft.fillScreen(TFT_BLACK);
  
  u8f.begin(tft);
  u8f.setFont(u8g2_font_wqy16_t_gb2312); 
  u8f.setFontMode(1);                    
  u8f.setForegroundColor(TFT_GREEN);     
  
  Wire.begin(17, 18); 
  ts.begin();
  
  moveArm(homePos,2000);
  delay(1000);
  
  tft.fillScreen(TFT_BLACK);
  isSleeping = true;
  drawCyberEyes(true);
}

void sendServoCmd(int id, int pwm, int time) {
  char cmd[32]; sprintf(cmd, "#%03dP%04dT%04d!", id, pwm, time);
  ZlinkSerial.print(cmd); 
}

void moveArm(int* targetPWM, int time) {
  for(int i = 0; i < 4; i++) { sendServoCmd(i + 1, targetPWM[i], time); delay(30); }
}

void performAction(String act) {
  if (act == "retract") moveArm(homePos, 1500);
  else if (act == "extend") moveArm(extendPos, 1200);
  else if (act == "standby") moveArm(standbyPos, 1500);
  else if (act == "nod") { 
    sendServoCmd(3, 1100, 400); sendServoCmd(4, 2000, 400); delay(450);
    sendServoCmd(3, 700, 400); sendServoCmd(4, 1500, 400); 
  }
  else if (act == "shake") { 
    sendServoCmd(1, 1800, 450); delay(500);
    sendServoCmd(1, 1400, 450); delay(500);
    sendServoCmd(1, 1600, 450);
  }
}

// 👁️ 赛博眼渲染引擎 (新增)
void drawCyberEyes(bool open) {
  // 只擦除眼睛所在的区域，防止全屏闪烁瞎眼
  tft.fillRect(70, 100, 340, 100, TFT_BLACK);

  int eyeH = open ? 45 : 6; // 睁眼高度 45，闭眼高度 6（只剩一条缝）
  int yPos = 150 - (eyeH / 2); // 保持中心 Y 轴对称
  
  // 画左眼（外部边框 + 内部实体）
  tft.drawRect(85, 120, 100, 60, TFT_DARKGREEN);
  tft.fillRect(95, yPos, 80, eyeH, TFT_GREEN);

  // 画右眼（外部边框 + 内部实体）
  tft.drawRect(295, 120, 100, 60, TFT_DARKGREEN);
  tft.fillRect(305, yPos, 80, eyeH, TFT_GREEN);
}

// 🖼️ 正常的聊天 UI 引擎
void renderUI(const char* sender, const char* msg) {
  tft.fillScreen(TFT_BLACK);
  tft.drawRect(5, 5, 470, 310, TFT_GREEN);
  tft.fillRect(5, 5, 470, 45, TFT_DARKGREEN);
  
  u8f.setForegroundColor(TFT_WHITE);
  u8f.setCursor(20, 32); 
  u8f.print(sender);
  
  u8f.setForegroundColor(TFT_GREEN);
  
  String content = String(msg);
  int startIdx = 0;
  int newLineIdx = content.indexOf('\n');
  int currentY = 90; 

  // 🚨 增强第三步：使用 c_str() 确保字符串渲染更稳定
  while (newLineIdx != -1) {
    u8f.setCursor(20, currentY);
    u8f.print(content.substring(startIdx, newLineIdx).c_str());
    currentY += 30; 
    startIdx = newLineIdx + 1;
    newLineIdx = content.indexOf('\n', startIdx);
  }
  u8f.setCursor(20, currentY);
  u8f.print(content.substring(startIdx).c_str()); 
}

void loop() {
  if (Serial.available()) {
    String jsonStr = Serial.readStringUntil('\n');
    
    // 🚨 增强第四步：将 JSON 解析缓冲区从 512 翻倍到 1024
    StaticJsonDocument<1024> doc; 
    DeserializationError error = deserializeJson(doc, jsonStr);

    if (!error) {
      const char* cmd = doc["cmd"];
      if (strcmp(cmd, "action") == 0) {
        performAction(doc["val"]);
      } 
      else if (strcmp(cmd, "print") == 0) {
        String msgStr = String((const char*)doc["msg"]);
        
        // 🚨 核心修复：只要 Python 发来 SLEEPING 或 STANDBY，统统画眼睛！
        if (msgStr.indexOf("SLEEPING...") != -1 || msgStr.indexOf("STANDBY") != -1) {
          isSleeping = true;
          tft.fillScreen(TFT_BLACK);
          drawCyberEyes(true);
          lastBlinkTime = millis();
        } else {
          isSleeping = false;
          renderUI(doc["sender"], doc["msg"]);
        }
      }
    } else {
      // 如果解析失败，在串口打印出来，方便我们抓虫
      Serial.print("JSON Error: ");
      Serial.println(error.c_str());
    }
  }

  // 👁️ 2. 独立的心跳眨眼逻辑 (无阻塞)
  if (isSleeping) {
    unsigned long currentMillis = millis();
    // 睁眼状态，且达到了随机等待时间，该闭眼了
    if (eyesOpen && currentMillis - lastBlinkTime > nextBlinkDelay) {
      eyesOpen = false;
      drawCyberEyes(false); 
      lastBlinkTime = currentMillis;
    } 
    // 闭眼状态，保持 150 毫秒后迅速睁开
    else if (!eyesOpen && currentMillis - lastBlinkTime > 150) {
      eyesOpen = true;
      drawCyberEyes(true);
      lastBlinkTime = currentMillis;
      // 随机生成下一次眨眼的时间 (2秒到5秒之间)，看起来更像活物！
      nextBlinkDelay = random(2000, 5000); 
    }
  }

  // 3. 触摸反馈
  FT6336U_TouchPointType tp = ts.scan();
  if (tp.touch_count > 0) {
    int curX = map(tp.tp[0].y, 0, 480, 0, 480);
    int curY = map(tp.tp[0].x, 0, 320, 320, 0);
    Serial.printf("{\"event\":\"touch\",\"x\":%d,\"y\":%d}\n", curX, curY);
    delay(500);
  }
}