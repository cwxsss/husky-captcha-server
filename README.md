# 🐕 Husky Captcha Server (哈士奇验证码识别服务端)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

高性能通用验证码识别服务端。支持普通图形验证码（英数/中文/混合）、算术方程式自动计算，以及滑块拼图缺口位移计算。完全兼容「哈士奇网页验证码识别工具」油猴脚本协议，无缝即插即用，彻底解除云端每日 50 次额度限制与强制更新拦截。

---

## ✨ 核心特性

- ⚡ **高性能异步架构**：基于 **FastAPI + Uvicorn** 构建，吞吐量高、毫秒级响应。
- 🔤 **全能字符 OCR**：基于 `ddddocr` 神经网络，高精度识别英文字母（大小写）、纯数字、汉字混合字符。
- ➕ **智能算术方程式求解**：内置算术解析引擎，自动对 `3+5=?`、`12*4`、`八减三等于几` 等公式进行求解并返回计算数值。
- 🧩 **滑块拼图双引擎匹配**：
  - **引擎 A (`ddddocr slide_match`)**：针对常规带缺口阴影滑块。
  - **引擎 B (`OpenCV Canny + Template Match`)**：针对自定义透明通道拼图块，结合边缘特征精准计算 $X$ 轴位移。
  - **自动缩放适配**：自动根据网页展示比例 (`backgroundDisplayWidth`) 计算精确 CSS 滑动像素。
- 🛡️ **双协议透明解密中间件**：支持油猴脚本内置的 `fnv1a32-xorshift32` 动态加密负载，无论是加密调用还是普通 JSON 调用均可原生兼容。
- 🖥️ **现代可视化控制台**：浏览器直接打开 `http://<服务器IP>:7070`，即可进行验证码上传测试、滑块缺口计算、查看服务状态。
- 📦 **开箱即用油猴脚本 (v8.00)**：内置配套油猴脚本，支持在油猴菜单随时修改服务器地址，解除强制升级锁。

---

## 🚀 快速启动

### 方案一：Docker 一键部署（推荐）

确保服务器已安装 Docker 与 Docker Compose：

```bash
# 1. 克隆代码仓库
git clone https://github.com/cwxsss/husky-captcha-server.git
cd husky-captcha-server

# 2. 一键构建并启动
docker compose up -d --build
```

或者直接执行一键脚本：
```bash
chmod +x deploy.sh && ./deploy.sh
```

服务将在 `0.0.0.0:7070` 启动，浏览器访问 `http://<你的服务器IP>:7070` 即可进入 Web 测试控制台。

---

### 方案二：宿主机 Python 直接运行

```bash
# 1. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate # Windows

# 2. 安装依赖 (Ubuntu/Debian 建议提前安装系统库: apt-get install -y libgl1 libglib2.0-0 libgomp1)
pip install -r requirements.txt

# 3. 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 7070 --reload
```

---

## 📦 油猴脚本安装与配置

1. 打开浏览器 Tampermonkey（油猴）扩展。
2. 安装仓库内自带的 `userscript/husky-captcha.user.js`（或启动服务后在浏览器直接访问 `http://<你的服务器IP>:7070/userscript/husky-captcha.user.js` 安装）。
3. 安装完成后，**脚本默认连接官方默认服务器**（开箱即用，无需配置）。
4. 如需连接您的自建专属服务器：
   - 在任意网页上，点击浏览器右上角 Tampermonkey（油猴）插件图标。
   - 在弹出的菜单列表中点击：**「⚙️ 设置识别服务器地址」**。
   - 输入您的自建服务器完整地址（例如 `http://<你的服务器IP>:7070` 或 `http://localhost:7070`），点击确定。
   - 刷新当前网页即可生效！如需恢复官方服务器，再次点击该菜单留空保存即可。
5. **完整原生功能菜单支持**：
   - ⚙️ **设置识别服务器地址**：随时切换官方默认服务与自建专属服务。
   - 📋 **管理黑/白名单**：支持通配符与正则表达式，按网址灵活配置识别黑名单与白名单。
   - ⚙️ **其他设置（Other settings）**：支持调整语言、配置额度码、自定义规则等。
   - 🎯 **【普通】手动绑定验证码和输入框**：针对非标准网页，一键手动选取识别目标与输入框。
   - 🧩 **【滑块】手动绑定滑块验证码**：手动圈选背景图、滑块与缺口。
   - 🩺 **常见问题与诊断**：一键生成诊断报告。
   - 🧹 **清空当前网站数据**：快速重置当前站点的识别绑定与配置。

---

## 📡 API 接口规范

### 1. 通用字符/算术验证码识别

* **URL**: `POST /captcha`
* **Content-Type**: `application/json`
* **Request Body**:
  ```json
  {
    "image": "data:image/png;base64,iVBORw0KGgo...",
    "type": "general" // 支持 "general", "numeric", "chinese", "math"
  }
  ```
* **Response**:
  ```json
  {
    "ok": true,
    "data": {
      "value": "8",
      "captcha_type": "general",
      "request_id": "req_1729648291000",
      "daily_request_limit": 999999,
      "daily_request_remaining": 999999,
      "daily_request_used": 1
    }
  }
  ```

### 2. 滑块拼图验证码缺口计算

* **URL**: `POST /api/slide/solve` 或 `POST /slideCaptcha`
* **Content-Type**: `application/json`
* **Request Body**:
  ```json
  {
    "backgroundImage": "data:image/png;base64,iVBORw0KGgo...",
    "targetImage": "data:image/png;base64,iVBORw0KGgo...",
    "backgroundDisplayWidth": 300
  }
  ```
* **Response**:
  ```json
  {
    "ok": true,
    "data": {
      "distance": 142.5,
      "target": [142.5, 80],
      "method": "ddddocr"
    }
  }
  ```

---

## 🛠️ 项目目录结构

```
husky-captcha-server/
├── app/
│   ├── main.py              # FastAPI 主程序入口与解密中间件
│   ├── config.py            # 全局配置参数
│   ├── core/
│   │   ├── crypto.py        # XOR+FNV1a32 协议透明解密/加密
│   │   ├── ocr_engine.py    # ddddocr 识别引擎与图像增强预处理
│   │   ├── math_solver.py   # 智能方程式求解器
│   │   └── slide_matcher.py # OpenCV + ddddocr 滑块位移匹配
│   ├── api/
│   │   ├── captcha.py       # /captcha 识别接口
│   │   ├── slide.py         # /api/slide/solve 滑块接口
│   │   ├── config_routes.py # /api/userscript/config 配置下发
│   │   └── telemetry.py     # 埋点与健康监控
│   └── static/
│       └── index.html       # Web 可视化测试仪表盘
├── userscript/
│   └── husky-captcha.user.js # 配套油猴脚本 (v8.00 自建版)
├── Dockerfile               # 容器化构建文件
├── docker-compose.yml       # Docker Compose 一键拉起
├── requirements.txt         # 核心依赖清单
├── deploy.sh                # Linux VPS 一键部署脚本
└── README.md
```

---

## 📄 License

MIT License © 2026
