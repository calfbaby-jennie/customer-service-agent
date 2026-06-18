# Customer Service Agent - 智能客服系统

一个基于多 Agent 协作的企业级智能客服系统。通过 LangGraph、FastAPI 和 LLM 的结合，实现工单的智能分类、处理和评估。

## 核心特性

- **多 Agent 架构**：Supervisor + Policy + Action + Critic 四层设计
- **灵活的 LLM 支持**：支持 OpenAI、Claude、本地 Ollama 等多种模型切换
- **Mac 本地开发友好**：SQLite + 最佳实践配置
- **快速 MVP 验证**：最小化的代码框架，快速上手
- **企业级扩展性**：代码结构支持后续升级到生产环境

## 快速开始

### 1. 克隆/复制项目

```bash
git clone <your-repo>
cd customer-service-agent
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY
```

### 5. 初始化数据库

```bash
python src/database/init_db.py
```

### 6. 启动应用

```bash
python -m uvicorn src.api.main:app --reload
```

打开 http://localhost:8000/ui

### 7. 本地测试（不启动服务器）

```bash
python test_local.py
```

## 项目结构

```
customer-service-agent/
├── .env.example              # 环境变量示例
├── .gitignore
├── README.md
├── requirements.txt
├── test_local.py             # 本地测试脚本
│
├── src/
│   ├── __init__.py
│   │
│   ├── models/               # 数据模型和 LLM 提供者
│   │   ├── __init__.py
│   │   ├── llm_provider.py   # LLM 抽象层（支持多模型切换）
│   │   └── schemas.py        # Pydantic 数据模型
│   │
│   ├── database/             # 数据库配置和模型
│   │   ├── __init__.py
│   │   ├── connection.py     # Mac SQLite 连接管理
│   │   ├── models.py         # SQLAlchemy ORM 模型
│   │   └── init_db.py        # 数据库初始化脚本
│   │
│   ├── agents/               # 四个 Agent 的实现
│   │   ├── __init__.py
│   │   ├── supervisor.py     # 工单分类与路由
│   │   ├── policy.py         # 工作流规划
│   │   ├── action.py         # 执行决策生成建议
│   │   ├── critic.py         # 质量评估
│   │   └── executor.py       # 整合执行引擎
│   │
│   ├── tools/                # 工具集成
│   │   ├── __init__.py
│   │   ├── order_system.py   # 订单系统集成
│   │   ├── knowledge_base.py # 知识库查询
│   │   └── registry.py       # 工具注册表
│   │
│   ├── api/                  # FastAPI 应用
│   │   ├── __init__.py
│   │   ├── routes.py         # API 路由
│   │   └── main.py           # 应用入口
│   │
│   └── utils/                # 工具函数
│       ├── __init__.py
│       └── config.py         # 配置管理
│
├── templates/                # Web UI
│   └── index.html
│
└── tests/
    └── test_agents.py        # 单元测试
```

## 核心概念

### 四个 Agent

1. **Supervisor Agent**：理解工单内容，进行分类和路由
2. **Policy Agent**：任务分解，制定处理工作流
3. **Action Agent**：执行具体操作，生成处理建议
4. **Critic Agent**：评估建议质量，决策是否自动发送

### LLM 灵活支持

支持多种 LLM 模型，随时切换：

```python
from src.models.llm_provider import get_llm_provider

# 切换到 GPT-4
llm = get_llm_provider("gpt4")

# 切换到本地 Ollama
llm = get_llm_provider("ollama_llama")

# 切换到 Claude
llm = get_llm_provider("claude")
```

### 数据库

- Mac 本地开发：SQLite（自动存储在 `~/.local/share/customer-service-agent/`）
- 支持后期升级到 PostgreSQL
- SQLAlchemy ORM，易于扩展

## API 端点

```
POST   /tickets              # 处理工单
GET    /tickets/{id}         # 查询工单详情
GET    /stats                # 获取统计信息
GET    /health               # 健康检查
GET    /ui                   # Web 界面
```

## 使用示例

### 通过 API 提交工单

```bash
curl -X POST http://localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-001",
    "order_id": "ORD-12345",
    "content": "我的订单已经一周还没收到，想退货"
  }'
```

### 本地 Python 测试

```python
import asyncio
from src.agents.executor import run_agent_pipeline

async def test():
    state = await run_agent_pipeline(
        ticket_id="TEST-001",
        ticket_content="我想退货"
    )
    print(f"分类：{state['classification']}")
    print(f"评分：{state['eval_score']}")
    print(f"决策：{state['final_action']}")

asyncio.run(test())
```

## 配置说明

### .env 变量

- `OPENAI_API_KEY`: OpenAI API 密钥
- `ANTHROPIC_API_KEY`: Claude API 密钥
- `DEFAULT_LLM`: 默认使用的 LLM 模型
- `DATABASE_URL`: 数据库连接字符串
- `DEBUG`: 调试模式
- `LOG_LEVEL`: 日志级别

### LLM 模型选择

在 `src/models/llm_provider.py` 中配置：

```python
LLM_CONFIGS = {
    "gpt4": LLMConfig(provider="openai", model="gpt-4"),
    "gpt35": LLMConfig(provider="openai", model="gpt-3.5-turbo"),
    "ollama_llama": LLMConfig(provider="ollama", model="llama2"),
    "claude": LLMConfig(provider="claude", model="claude-3-sonnet"),
}
```

## 常见问题

### Q: 如何使用本地 Ollama？

A: 首先安装 Ollama，然后：

```bash
ollama run llama2
```

在代码中切换：

```python
llm = get_llm_provider("ollama_llama")
```

### Q: 如何连接真实的订单系统？

A: 编辑 `src/tools/order_system.py`，实现真实的数据库查询或 API 调用。

### Q: 如何添加新的工具？

A: 在 `src/tools/` 目录下创建新文件，然后在 `registry.py` 中注册。

## 后续扩展

### 升级到生产环境

1. 数据库从 SQLite 升级到 PostgreSQL
2. 添加 Langfuse 可观测性集成
3. 部署到 Kubernetes
4. 添加企业级认证（SSO/LDAP）
5. 实现混合 LLM 路由（敏感数据本地，非敏感数据云端）

### 支持更多工单类型

编辑各个 Agent 的提示词，或添加新的工单分类逻辑。

## 许可证

MIT

## 联系方式

有问题？提交 Issue 或 PR。
