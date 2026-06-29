"""
FastAPI application entrypoint.
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .routes import router
from ..database.init_db import init_database


init_database()

app = FastAPI(
    title="Customer Service Agent",
    description="智能客服 Agent 系统",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Customer Service Agent API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Customer Service Agent</title>
  <style>
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f7f8fa; color: #1f2937; }
    main { max-width: 960px; margin: 0 auto; padding: 32px 20px; }
    h1 { font-size: 28px; margin: 0 0 20px; }
    section { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 16px; }
    label { display: block; font-size: 13px; font-weight: 600; margin: 12px 0 6px; }
    input, textarea { width: 100%; box-sizing: border-box; border: 1px solid #d1d5db; border-radius: 6px; padding: 10px 12px; font: inherit; }
    textarea { min-height: 120px; resize: vertical; }
    button { margin-top: 14px; border: 0; border-radius: 6px; padding: 10px 14px; background: #0f766e; color: white; font-weight: 700; cursor: pointer; }
    pre { white-space: pre-wrap; word-break: break-word; background: #111827; color: #f9fafb; border-radius: 8px; padding: 14px; min-height: 120px; }
  </style>
</head>
<body>
  <main>
    <h1>Customer Service Agent</h1>
    <section>
      <form id="ticket-form">
        <label for="customer_id">客户 ID</label>
        <input id="customer_id" name="customer_id" value="CUST-001" />
        <label for="order_id">订单 ID</label>
        <input id="order_id" name="order_id" value="ORD-12345" />
        <label for="content">工单内容</label>
        <textarea id="content" name="content">我的订单已经一周还没收到，想退货</textarea>
        <button type="submit">提交工单</button>
      </form>
    </section>
    <section>
      <pre id="result">等待提交...</pre>
    </section>
  </main>
  <script>
    const form = document.querySelector("#ticket-form");
    const result = document.querySelector("#result");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      result.textContent = "处理中...";
      const body = Object.fromEntries(new FormData(form).entries());
      const response = await fetch("/tickets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const data = await response.json();
      result.textContent = JSON.stringify(data, null, 2);
    });
  </script>
</body>
</html>
"""


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
