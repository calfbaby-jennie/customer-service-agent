# src/api/main.py
"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from ..database.init_db import init_database

# 初始化数据库
init_database()

# 创建应用
app = FastAPI(
    title="Customer Service Agent",
    description="智能客服 Agent 系统",
    version="0.1.0",
)

# 添加 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Customer Service Agent API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204) # 204无内容，不再报404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)