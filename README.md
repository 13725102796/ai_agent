# LitAgent - 智能文学创作助手 🚀

LitAgent 是一个基于 **LangGraph** 和 **FastAPI** 构建的智能写作 Agent，它通过模拟人类的创作心流（Search -> Strategize -> Write -> Edit），结合 **DeepSeek** 和 **Claude** 的能力，自动生成高质量、有深度、且具备真实数据支撑的文章。

![LitAgent Demo](https://via.placeholder.com/800x400?text=LitAgent+Demo+Capture)

## ✨ 核心特性

- **🔍 真实全网搜索 (Real-time Search)**: 集成 `DuckDuckGo` API，针对写作主题实时抓取网络最新资讯，并提供来源引用，拒绝幻觉。
- **🧠 深度策略思考 (Strategic Thinking)**: 策略师角色并非直接写作，而是分析研究资料，制定独特的“写作风格”（如犀利、诗意）和“文章结构”（如英雄之旅、SCQA），并向用户解释其决策依据。
- **✍️ 沉浸式写作流 (Flow State)**: 前端采用可视化“思考流”UI，实时展示 Agent 的每一个思考步骤（研究、策略、撰写、润色），让用户看到 AI 的“脑回路”。
- **🛑 实时控制 (Full Control)**: 支持随时中断生成任务，给用户完全的控制权。
- **📝 严格的编辑把关**: 编辑角色不仅负责润色文笔，还被编入了严格的字数控制和逻辑检查指令，确保输出符合预期。

## 🛠 技术栈

### Backend (后端)
- **Python 3.11+**
- **FastAPI**: 高性能 Web 框架，支持 SSE (Server-Sent Events) 流式输出。
- **LangGraph**: 构建多智能体协作（Multi-Agent Collaboration）的工作流图。
- **LangChain**: 基础 LLM 调用与工具封装。
- **DuckDuckGo Search**: 无需 API Key 的搜索工具。
- **Models**: 支持 DeepSeek V3 (主要写作) 和 Claude (辅助研究/策略)。

### Frontend (前端)
- **React**: 现代 UI 库。
- **Vite**: 极速构建工具。
- **TailwindCSS**: 原子化 CSS 样式。
- **Framer Motion**: 流畅的动画效果。
- **Lucide React**: 精美图标库。

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/lit-agent.git
cd lit-agent
```

### 2. 后端设置

```bash
cd backend

# 创建并激活虚拟环境 (可选)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制 .env.example 为 .env 并填入你的 API Key (DEEPSEEK_API_KEY 等)
cp .env.example .env

# 启动服务器 (包含端口冲突自动检测)
./run_backend.sh
```

后端服务将在 `http://localhost:8000` 启动。

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端页面通常在 `http://localhost:5173` 访问。

## 🔄 工作流详解

1.  **Researcher (研究员)**: 对用户输入的主题进行 3-5 次相关搜索，汇总关键信息和来源。
2.  **Strategist (策略师)**: 基于研究结果，决定文章的基调（Tone）和结构（Structure），并输出 `Rationale`（决策依据）。
3.  **Writer (作家)**: 接收策略师的指令和研究员的资料，进行长文撰写。
4.  **Editor (编辑)**: 对草稿进行最终打磨，优化词汇，检查字数，确保文章既优美又精准。

## 📄 License

MIT License
