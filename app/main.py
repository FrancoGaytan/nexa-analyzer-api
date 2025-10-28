from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.context import router as context_router

load_dotenv()

app = FastAPI(title=settings.app_name, debug=settings.debug, version=settings.version)

app.include_router(health_router)
app.include_router(context_router)

@app.get("/", tags=["root"])
async def root():
    return {"message": f"Welcome to {settings.app_name}"}
