# AI Resume Optimizer

AI Resume Optimizer 是一个面向求职场景的智能简历优化工具。项目支持在线生成和优化简历、上传头像、导出 PDF / Word / Markdown / TXT，并提供中英文界面切换、登录演示、招聘网站匹配建议和可选 OpenAI API 接入。

## 在线访问

生产环境地址：

https://ai-resume-optimizer-coral.vercel.app/

## 功能概览

- 智能简历生成：根据姓名、目标岗位、教育经历、项目经历、技能关键词等信息生成正式简历。
- 简历优化合并：生成和优化合并为一个工作流，可以从表单生成，也可以基于已有简历继续优化。
- 技能智能整理：将技能关键词改写成标准简历技能描述，并按框架、中间件/数据库、语言、工程工具等优先级排序。
- 项目经历结构化输入：每个项目可以展开填写项目介绍、项目架构、技术架构、个人职责，生成时会合并为紧凑真实的简历项目描述。
- 多项目支持：可以新增、删除多个项目，适合真实简历场景。
- 中英文切换：登录页、主界面、状态栏、输入占位内容、生成结果等支持中文和英文切换。
- 头像上传：支持上传个人照片，并在预览和导出时使用。
- 多格式导出：支持 PDF、Word DOCX、Markdown、TXT。
- 登录演示：支持邮箱验证码登录演示，以及微信/支付宝扫码登录演示。
- 招聘匹配投放：提供岗位平台、城市、薪资、关键词和简历匹配建议，生成合规投递计划。
- AI 模式选择：默认使用免费本地规则生成；付费模式需要用户主动输入自己的 OpenAI API Key。
- 历史记录：保存生成历史，方便回看和继续编辑。

## 当前说明

这个项目默认不会消耗 OpenAI 费用。免费模式使用本地规则和模板逻辑生成内容。只有用户在界面中选择付费 OpenAI API，并输入自己的 API Key 后，才会调用 OpenAI。

微信和支付宝登录目前是演示级扫码流程：二维码是真实可扫描的链接，会打开确认页并回写登录状态，但没有接入微信开放平台或支付宝开放平台的正式 OAuth 生产认证。

招聘网站匹配投放目前是合规建议和投递方案生成，不会绕过招聘平台规则，也不会自动批量投递。

## 技术栈

- 前端：Vue 3、Vite、Element Plus、Axios、QRCode
- 后端：FastAPI、Python、Pydantic
- 导出：python-docx、ReportLab、Pillow
- AI 接入：免费本地规则、可选 Ollama、可选 OpenAI API
- 部署：Vercel
- 数据：内存历史记录，预留 Supabase 集成

## 项目结构

```text
.
├── api/
│   └── index.py                 # Vercel Python Function 入口
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 路由
│   │   ├── models.py            # 请求和响应模型
│   │   └── services/
│   │       ├── ai_service.py    # 简历生成、优化、招聘匹配逻辑
│   │       ├── export_service.py # PDF / Word / 文本导出
│   │       └── history_store.py # 历史记录存储
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.vue              # 主应用界面
│   │   ├── api.js               # 前端 API 封装
│   │   ├── main.js
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docs/
├── pyproject.toml
├── requirements.txt
├── vercel.json
└── README.md
```

## 本地运行

### 1. 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

后端默认地址：

```text
http://localhost:8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认地址通常是：

```text
http://127.0.0.1:5173
```

## 环境变量

后端环境变量：

```text
AI_PROVIDER=free
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_TIMEOUT_SECONDS=45
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
PUBLIC_BASE_URL=
```

前端环境变量：

```text
VITE_API_BASE_URL=http://localhost:8000
```

线上 Vercel 部署时前端 API 默认使用同域名相对路径，不需要额外配置 `VITE_API_BASE_URL`。

## API 说明

主要接口：

- `POST /api/generate`：生成/优化简历或生成招聘匹配方案。
- `GET /api/history`：读取历史记录。
- `DELETE /api/history/{record_id}`：删除历史记录。
- `POST /api/export`：导出 PDF、DOCX、Markdown 或 TXT。
- `POST /api/auth/email-code`：生成邮箱验证码演示。
- `POST /api/auth/verify-code`：验证邮箱验证码。
- `POST /api/auth/qr-session`：创建扫码登录 session。
- `GET /api/auth/qr-session/{session_id}`：查询扫码登录状态。
- `GET /api/auth/qr-session/{session_id}/confirm-page`：扫码确认页面。

## 部署说明

项目已经部署到 Vercel：

https://ai-resume-optimizer-coral.vercel.app/

Vercel 配置在 `vercel.json` 中：

- 构建命令：`cd frontend && npm ci && npm run build`
- 输出目录：`frontend/dist`
- API 重写：`/api/(.*)` 转发到 `api/index.py`
- SPA 重写：其他路径转发到 `index.html`

部署过程中为了兼容 Vercel 当前 Python 构建环境，项目升级了后端依赖，并在构建环境中设置了 `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1`。

## GitHub 仓库

远程仓库：

https://github.com/Sy1mple/ai-resume-optimizer

当前主分支：

```text
main
```

## 后续可扩展方向

- 接入真实微信开放平台和支付宝开放平台登录。
- 接入真实招聘平台开放 API，做授权后的岗位搜索和投递管理。
- 增加用户账户系统和云端简历版本管理。
- 增加更多简历模板和行业模板。
- 增加 ATS 评分、岗位 JD 匹配、关键词差距分析。
- 增加 OpenAI、DeepSeek、通义千问、智谱等多模型选择。
