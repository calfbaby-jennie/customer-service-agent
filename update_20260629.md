# Customer Service Agent 更新记录

## 本次已修改

1. DeepSeek 改为默认 LLM
   - 修改 `src/models/llm_provider.py`
   - 默认 `DEFAULT_LLM=deepseek`
   - LiteLLM 模型名为 `deepseek/deepseek-chat`
   - 读取 `DEEPSEEK_API_KEY` 与可选 `DEEPSEEK_BASE_URL`
   - OpenAI / Claude 配置能力保留，但在 `LLM_CONFIGS` 中先注释掉

2. 修复 Agent import 阶段就要求 OpenAI Key 的问题
   - 原来 `supervisor.py`、`policy.py`、`action.py`、`critic.py` 顶层写死 `get_llm_provider("gpt35")`
   - 现在改为函数执行时读取默认 LLM，避免 API 启动时因缺少 OpenAI key 直接失败

3. 补齐多 Agent 工作流
   - `executor.py` 优先使用 LangGraph `StateGraph`
   - 如果本机未安装 LangGraph，自动降级为顺序执行 fallback，便于本地 smoke test
   - 流程保持：Supervisor -> Policy -> Action -> Critic

4. 补齐企业集成占位工具
   - 新增 `src/tools/`
   - 包含 CRM、订单系统、知识库、工单系统 mock adapter
   - 新增 `registry.py` 统一工具注册表，后续可替换为 Salesforce / ERP / Elasticsearch / Jira

5. 修复数据库初始化与配置
   - `connection.py` 开始读取 `.env` 中的 `DATABASE_URL`
   - `init_db.py` 同时支持：
     - `python -m src.database.init_db`
     - `python src/database/init_db.py`

6. 修复 API 与 README 不一致的问题
   - 新增 `/ui` 简易页面
   - `POST /tickets` 现在会把 `customer_id`、`order_id` 传入 Agent pipeline
   - 非退货/售后工单不再返回空字段，而是进入 `human_confirm`

7. 新增 `.env.example`
   - DeepSeek 默认配置
   - OpenAI / Claude key 注释示例
   - `DEFAULT_LLM=mock` 离线测试方式

8. 修复 `test_local.py` 的退出码
   - 原脚本即使所有工单失败也会退出码 0
   - 现在只要有失败就退出码 1，便于 CI 或本地脚本判断

## 原项目主要问题

1. LLM 默认配置不匹配
   - `.env` 中已有 `DEEPSEEK_API_KEY`，但代码固定调用 `gpt35`
   - 没有 `OPENAI_API_KEY` 时，导入 Agent 就会失败

2. README 与代码不一致
   - README 写了 `.env.example`，实际没有
   - README 写了 `/ui`，实际没有路由
   - README 写了 `src/tools/`，实际没有
   - README 写 LangGraph 编排，但原 `executor.py` 是普通顺序调用

3. 数据库配置没有读取环境变量
   - `.env` 中的 `DATABASE_URL` 原本不会生效
   - 数据库路径固定到 `~/.local/share/customer-service-agent/app.db`

4. 数据库初始化命令会失败
   - README 推荐 `python src/database/init_db.py`
   - 原脚本使用相对导入，直接执行会报 `ImportError: attempted relative import with no known parent package`

5. 非退货工单响应字段可能为空
   - 原流程中 Policy 设置 `skip`
   - Critic 又把没有 recommendation 的状态改成 `reject`
   - API response_model 要求 `eval_score`、`recommendation` 是非空字段，容易触发响应校验问题

6. 本地测试依赖真实三方库和真实 LLM
   - 没装 `litellm` 时 `test_local.py` 无法导入
   - 现在提供 `DEFAULT_LLM=mock` 做离线 smoke test

7. 本地测试失败不反映到进程退出码
   - 原脚本捕获异常后继续执行，最后仍返回 0
   - 自动化测试会误判为成功

## 怎么测试

### 1. 安装依赖

```bash
cd /Users/daozhu/workspace/customer-service-agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. 配置 DeepSeek

```bash
cp .env.example .env
```

编辑 `.env`：

```bash
DEFAULT_LLM=deepseek
DEEPSEEK_API_KEY=你的 DeepSeek Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DATABASE_URL=sqlite:///./data/app.db
```

注意：`.env` 中不要写成 `DEFAULT_LLM=deepseek  # 注释`，虽然代码已做兼容，但更推荐把注释放到单独一行。

### 3. 初始化数据库

```bash
python -m src.database.init_db
```

或：

```bash
python src/database/init_db.py
```

### 4. 离线 smoke test

不触网、不依赖真实 LLM：

```bash
DEFAULT_LLM=mock python test_local.py
```

预期结果：

- 退货/退款类工单分类为 `退货`
- Critic 评分约 86
- 最终决策为 `auto_send`
- 普通咨询类工单进入 `human_confirm`

### 5. DeepSeek 真实调用测试

```bash
python test_local.py
```

如果失败，优先检查：

- `DEEPSEEK_API_KEY` 是否存在
- `DEFAULT_LLM` 是否为 `deepseek`
- 网络是否能访问 DeepSeek API
- `litellm` 是否安装成功

### 6. 启动 API

```bash
python -m uvicorn src.api.main:app --reload
```

健康检查：

```bash
curl http://localhost:8000/health
```

提交工单：

```bash
curl -X POST http://localhost:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-001",
    "order_id": "ORD-12345",
    "content": "我的订单已经一周还没收到，想退货"
  }'
```

浏览器访问：

```text
http://localhost:8000/ui
```

## 本次验证结果

我在当前机器的全局 Python 环境下执行了以下检查：

```bash
python3 -B -c "from pathlib import Path; import ast; [ast.parse(p.read_text()) for p in Path('src').rglob('*.py')]; ast.parse(Path('test_local.py').read_text()); print('syntax ok')"
```

结果：通过，输出 `syntax ok`。

```bash
DEFAULT_LLM=mock python3 -B test_local.py
```

结果：通过，3 条测试工单全部成功；两条退货/退款工单进入 `auto_send`，一条配送咨询进入 `human_confirm`。

```bash
python3 -B -c "from src.models.llm_provider import get_llm_provider; p=get_llm_provider(); print(p.model_name)"
```

结果：通过，输出 `deepseek/deepseek-chat`。

```bash
python3 -B test_local.py
```

结果：未通过，当前全局 Python 未安装 `litellm`，需要先安装 `requirements.txt`。这是依赖缺失，不是 Agent 链路逻辑错误。

```bash
python3 -B src/database/init_db.py
python3 -B -m src.database.init_db
```

结果：都不再报相对导入错误；当前失败点是全局 Python 未安装 `sqlalchemy`，安装依赖后再执行即可。

## 这次未完成但建议后续做

1. 加 pytest 单元测试，覆盖四个 Agent 与 API route
2. 加真实 Tool Adapter：Salesforce、ERP/Oracle、Elasticsearch、Jira
3. 加 Langfuse + OpenTelemetry trace，把每个 Agent 的 tokens、成本、延迟写入日志
4. 加 DeepEval 离线评估集，沉淀 Critic 分数与人工反馈
5. 增加 Alembic migration，避免生产环境直接 `create_all`
6. 增加字段级加密、脱敏日志、审计日志与鉴权
