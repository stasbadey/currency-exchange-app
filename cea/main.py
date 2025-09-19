from fastapi import FastAPI
from api.routers import router

app = FastAPI(title="Currency Exchange Service")

# Подключаем маршруты
app.include_router(router)

@app.get("/ping")
async def ping():
    return {"status": "ok"}
