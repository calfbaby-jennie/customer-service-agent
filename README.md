# Customer Service Agent - 智能客服 Agent 系统

面向电商退货/售后工单的多 Agent 协作系统。项目采用 Supervisor + Policy + Action + Critic 四层架构，默认接入 DeepSeek API，并保留 OpenAI 与 Claude 的扩展能力。

## 核心特性

- **四层 Agent 架构**：Supervisor 负责意图理解与路由，Policy 负责任务分解，Action 负责工具编排与建议生成，Critic 负责质量评估与最终决策
- **DeepSeek 优先**：默认使用 `deepseek/deepseek-chat`，通过 LiteLLM 统一调用
- **多模型扩展**：OpenAI / Claude 配置已保留在 `src/models/llm_provider.py` 中，默认注释
- **状态机编排**：安装 LangGraph 后自动使用 StateGraph；未安装依赖时可用顺序 fallback 做本地 smoke test
- **企业集成占位**：提供 CRM、订单、知识库、工单系统的本地 mock adapter，后续可替换为 Salesforce、ERP/Oracle、Elasticsearch、Jira
- **本地开发友好**：支持 SQLite，`DATABASE_URL` 可从 `.env` 配置

## 快速开始

### 1. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安装依赖

```bash
python -m pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入 DeepSeek 配置：

```bash
DEFAULT_LLM=deepseek
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DATABASE_URL=sqlite:///./data/app.db
```

### 4. 初始化数据库

两种方式都支持：

```bash
python -m src.database.init_db
# 或
python src/database/init_db.py
```

### 5. 启动 API

```bash
python -m uvicorn src.api.main:app --reload
```

打开：

- API health check: http://localhost:8000/health
- 简易 UI: http://localhost:8000/ui

### 6. 本地测试

使用真实 DeepSeek：

```bash
python test_local.py
```

不触网 smoke test：

```bash
DEFAULT_LLM=mock python test_local.py
```

## API 示例

```bash
curl -X POST http://localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-001",
    "order_id": "ORD-12345",
    "content": "我的订单已经一周还没收到，想退货"
  }'
```

## 项目结构

```text
customer-service-agent/
├── .env.example
├── README.md
├── requirements.txt
├── test_local.py
└── src/
    ├── agents/
    │   ├── supervisor.py
    │   ├── policy.py
    │   ├── action.py
    │   ├── critic.py
    │   └── executor.py
    ├── api/
    │   ├── main.py
    │   └── routes.py
    ├── database/
    │   ├── connection.py
    │   ├── init_db.py
    │   └── models.py
    ├── models/
    │   ├── llm_provider.py
    │   └── schemas.py
    └── tools/
        ├── crm.py
        ├── order_system.py
        ├── knowledge_base.py
        ├── ticket_system.py
        └── registry.py
```

## LLM 配置

当前默认：

```python
"deepseek": LLMConfig(
    provider="deepseek",
    model="deepseek-chat",
    api_key_env="DEEPSEEK_API_KEY",
    base_url_env="DEEPSEEK_BASE_URL",
)
```

OpenAI / Claude 配置保留在同一文件中，默认注释；需要切换时取消注释并设置 `.env`：

```bash
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
DEFAULT_LLM=gpt4o_mini
# 或 DEFAULT_LLM=claude_sonnet
```

## 决策分层

- `auto_send`：Critic 评分 >= 85 且允许自动发送
- `human_confirm`：评分 >= 60，或非退货/售后工单转人工确认
- `reject`：评分低于 60，或建议生成失败

## 后续生产化方向

- 将 `src/tools/` 下 mock adapter 替换为 Salesforce、ERP/Oracle、Elasticsearch、Jira 的真实客户端
- 接入 Langfuse + OpenTelemetry，把 `execution_logs` 扩展为 Trace、成本、延迟指标
- 接入 DeepEval，把 Critic 评分沉淀为离线评估集与微调数据
- 数据库从 SQLite 切换 PostgreSQL，并补充 Alembic migration
- 增加鉴权、审计日志、字段级加密与敏感数据本地模型路由
