# 法援通 — 婚姻家庭法律咨询 AI 助手

**法援通**是一款基于 RAG（检索增强生成）技术的婚姻家庭法律知识科普 AI 助手，面向普通公众提供离婚纠纷、子女抚养、财产分割、家庭暴力、继承纠纷、彩礼返还等领域的法律知识咨询。系统通过语义检索精准匹配法律条文、司法解释和裁判案例，结合大语言模型生成通俗易懂的结构化回复，帮助非法律专业人士快速理解自身法律处境与可行方案。

> ⚠️ 本项目提供的是公共法律教育信息，不构成法律意见。如需正式法律帮助，请咨询专业律师或拨打 12348 法律援助热线。

---

## 核心功能

- **RAG 语义检索**：基于 ChromaDB 向量数据库 + BGE 中文 Embedding 模型，从 290 个法律知识 chunk 中精准检索相关法条、司法解释和裁判案例，动态注入 LLM 提示词
- **结构化对话流程**：信息收集阶段（系统化追问关键信息）→ 最终回复阶段（情况概述 + 法律规定 + 解决方案 + 案例参考 + 免责声明），两阶段分离，避免信息冗余
- **个性化响应**：根据用户性别、争议类型动态调整回复内容和措辞，如男性家暴受害者提供针对性支持、抚养权咨询不预设父母角色归属
- **紧急安全检测**：识别家庭暴力关键词后自动触发紧急联系信息（110、12338、12348），并根据受害者性别提供差异化求助渠道
- **意图边界守卫**：自动判断用户问题是否属于婚姻家庭法律范畴，超出范围时温和引导回相关领域
- **交互式选项**：信息收集阶段提供快捷选项，降低用户输入门槛，提升对话效率

---

## 技术栈

### 后端

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| Web 框架 | FastAPI + Uvicorn |
| LLM 集成 | OpenAI SDK（兼容 DeepSeek API） |
| Embedding 模型 | BAAI/bge-small-zh-v1.5（512 维） |
| 向量数据库 | ChromaDB（持久化存储） |
| Embedding 框架 | sentence-transformers |
| 数据验证 | Pydantic v2 + pydantic-settings |

### 前端

| 类别 | 技术 |
|------|------|
| 语言 | TypeScript |
| 框架 | React 19 |
| 构建工具 | Vite 8 |
| Markdown 渲染 | react-markdown + remark-gfm |

### 数据与工具

| 类别 | 技术 |
|------|------|
| 数据采集 | Python 爬虫（Snail 模块） |
| 数据格式 | JSON / JSONL / TXT |
| 向量数据库初始化 | 自定义 init_rag.py 脚本 |

---

## 项目结构

```
marriage_agent/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/                # API 路由
│   │   │   ├── chat.py         # 对话接口（核心）
│   │   │   └── feedback.py     # 反馈接口
│   │   ├── core/               # 核心逻辑
│   │   │   ├── rag_retriever.py    # RAG 检索模块
│   │   │   ├── slot_manager.py     # 对话槽位管理
│   │   │   ├── intent_guard.py     # 意图边界守卫
│   │   │   ├── emergency.py        # 紧急安全检测
│   │   │   └── heuristic.py        # 卡顿检测与引导
│   │   ├── llm/                # LLM 集成
│   │   │   ├── client.py       # LLM 客户端
│   │   │   └── prompts.py      # 系统提示词
│   │   ├── data/               # 数据与向量库
│   │   │   ├── chroma_db/      # ChromaDB 持久化存储
│   │   │   ├── laws.py         # 法条备用数据
│   │   │   └── cases.py        # 案例备用数据
│   │   ├── config.py           # 配置管理
│   │   └── main.py             # 应用入口
│   ├── scripts/
│   │   └── init_rag.py         # RAG 向量数据库初始化脚本
│   └── requirements.txt
│
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── components/
│   │   │   └── Chat.tsx        # 对话界面组件
│   │   ├── api.ts              # API 调用封装
│   │   ├── types.ts            # 类型定义
│   │   └── App.tsx
│   ├── vite.config.ts
│   └── package.json
│
├── Snail/                      # 数据采集工具集
│   ├── spiders/
│   │   ├── law_spider.py       # 法律条文爬虫
│   │   ├── judicial_spider.py  # 司法解释爬虫
│   │   └── case_spider.py      # 裁判案例采集
│   ├── utils/
│   │   ├── validator.py        # 格式验证与元数据管理
│   │   ├── logger.py           # 日志模块
│   │   └── request_helper.py   # HTTP 请求辅助
│   ├── config.py
│   ├── run_all.py              # 全量采集入口
│   └── migrate_to_rag.py       # 数据迁移至 RAGdata
│
├── RAGdata/                    # RAG 规范化数据
│   ├── 法律条文/
│   │   ├── law_articles.json   # 134 个法条 chunk
│   │   └── raw/                # 原始 txt 副本
│   ├── 司法解释/
│   │   ├── judicial_interpretations.json  # 141 个司法解释 chunk
│   │   └── raw/
│   ├── 裁判案例/
│   │   ├── court_cases.json    # 15 个案例 chunk
│   │   └── raw/
│   ├── all_chunks.jsonl        # 全量合并（290 条）
│   └── manifest.json           # 数据清单
│
└── Collected legal data/       # 原始采集数据
    ├── 法律条文/                # 134 个 txt
    ├── 司法解释/                # 3 个 txt
    ├── 裁判案例/                # 15 个 txt
    └── metadata.json
```

---

## 安装与配置

### 环境要求

| 依赖 | 版本要求 |
|------|---------|
| Python | >= 3.11 |
| Node.js | >= 18 |
| Conda | 推荐 Miniconda |
| Git | 任意版本 |

### 1. 克隆仓库

```bash
git clone https://github.com/<your-username>/marriage_agent.git
cd marriage_agent
```

### 2. 后端配置

```bash
# 创建并激活 conda 虚拟环境
conda create -n agent python=3.11 -y
conda activate agent

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装 RAG 额外依赖（chromadb 已包含在 requirements.txt 中）
pip install chromadb sentence-transformers
```

创建 `backend/.env` 文件：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

| 环境变量 | 必填 | 说明 |
|---------|------|------|
| `LLM_API_KEY` | ✅ | LLM API 密钥（支持 DeepSeek / OpenAI 兼容接口） |
| `LLM_BASE_URL` | 否 | API 基础地址，默认 `https://api.deepseek.com/v1` |
| `LLM_MODEL` | 否 | 模型名称，默认 `deepseek-chat` |
| `LLM_TEMPERATURE` | 否 | 生成温度，默认 `0.7` |
| `LLM_MAX_TOKENS` | 否 | 最大生成 token 数，默认 `2048` |
| `CORS_ORIGINS` | 否 | 允许的跨域来源，逗号分隔 |

### 3. 初始化 RAG 向量数据库

```bash
# 确保在 backend/ 目录下，agent 环境已激活
python scripts/init_rag.py
```

该脚本将：
- 加载 `RAGdata/` 中的 290 个 chunk
- 使用 bge-small-zh-v1.5 模型生成 512 维向量
- 写入 ChromaDB 持久化存储至 `backend/app/data/chroma_db/`

> 首次运行将自动下载 Embedding 模型（约 100MB），后续运行使用缓存。

### 4. 前端配置

```bash
cd frontend
npm install
```

---

## 使用指南

### 启动服务

**启动后端**（终端 1）：

```bash
cd backend
conda activate agent
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**启动前端**（终端 2）：

```bash
cd frontend
npm run dev
```

访问 http://localhost:5173 即可使用。

### API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/chat` | 发送对话消息 |
| `POST` | `/api/option` | 选择快捷选项 |
| `POST` | `/api/feedback` | 提交用户反馈 |
| `GET` | `/api/health` | 健康检查 |

#### 对话接口示例

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "我想离婚，丈夫经常打我", "session_id": "user_001"}'
```

响应：

```json
{
  "reply": "为了给您更准确的建议，我还需要了解：您的性别、目前居住安排...",
  "options": ["男性", "女性", "其他", "与配偶同住", "分居独住"],
  "is_emergency": true,
  "session_id": "user_001"
}
```

#### 反馈接口示例

```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user_001", "rating": "positive", "comment": "很有帮助"}'
```

### 典型使用场景

**场景 1：家庭暴力咨询**

1. 用户输入"我想离婚，丈夫经常打我"
2. 系统检测到家暴关键词，触发紧急安全提示（110、12338、12348）
3. 进入信息收集阶段，追问性别、居住安排、暴力类型
4. 信息收集完毕后，RAG 检索民法典第1079条、第1091条、反家暴法相关条文
5. 生成结构化回复：情况概述 → 法律规定 → 解决方案 → 案例参考 → 免责声明

**场景 2：彩礼返还咨询**

1. 用户输入"给了彩礼没结婚能要回来吗"
2. 系统追问性别、婚姻状态
3. RAG 检索彩礼司法解释、民法典婚姻家庭编相关条文
4. 生成包含具体法条解读和返还条件的回复

---

## 数据采集

如需更新法律数据，运行 Snail 采集模块：

```bash
cd Snail
conda activate agent
python -m Snail.run_all
```

采集完成后，迁移至 RAGdata 并重建向量索引：

```bash
python -m Snail.migrate_to_rag
cd ../backend
python scripts/init_rag.py
```

---

## 贡献规范

欢迎贡献！请遵循以下流程：

### 提交 Issue

- 使用 GitHub Issues 提交 Bug 报告或功能建议
- Bug 报告请包含：复现步骤、预期行为、实际行为、环境信息
- 功能建议请描述：使用场景、预期效果、可能的实现思路

### 提交 Pull Request

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "feat: add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request，描述变更内容和关联 Issue

### 代码风格

- **Python**：遵循 PEP 8，使用类型注解
- **TypeScript/React**：遵循 ESLint 配置，使用函数式组件
- **提交信息**：遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范
  - `feat:` 新功能
  - `fix:` 修复 Bug
  - `docs:` 文档变更
  - `refactor:` 代码重构
  - `chore:` 构建/工具变更

---

## 许可证

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

```
MIT License

Copyright (c) 2026 marriage_agent contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
