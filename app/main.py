from fastapi import FastAPI, Request, Depends, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from database import Base, engine
from controllers import router
from contextlib import asynccontextmanager


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# FastAPI 초기화
# Swagger UI와 ReDoc 문서를 비활성화
app = FastAPI(lifespan=app_lifespan, docs_url="/docs", redoc_url="/redoc")
app.add_middleware(SessionMiddleware, secret_key="kh333")
app.include_router(router)
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
