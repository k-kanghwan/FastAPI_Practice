from fastapi import FastAPI, Request, Depends, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from database import Base, engine
from controllers import router
from contextlib import asynccontextmanager

# offline Swagger UI 관련 임포트
import requests
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html


mode = "online"  # "online" 또는 "offline" 모드 설정
if requests.get("https://www.google.com").status_code != 200:
    mode = "offline"
print(f"\nSwagger UI 모드: {mode.capitalize()}\n")

if mode == "offline":
    DOCS_URL = None
    REDDOC_URL = None

elif mode == "online":
    DOCS_URL = "/docs"
    REDDOC_URL = "/redoc"


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# FastAPI 초기화
# Swagger UI와 ReDoc 문서를 비활성화
app = FastAPI(
    title=f"Hello API({mode.capitalize()} Swagger)",
    version="0.1.0",
    description="로컬 정적 Swagger UI 및 ReDoc 문서 예제",
    lifespan=app_lifespan,
    docs_url=DOCS_URL,
    redoc_url=REDDOC_URL,
)

app.add_middleware(SessionMiddleware, secret_key="kh333")
app.include_router(router)
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root(request: Request):
    return {"Hello": "World"}
    # return templates.TemplateResponse("home.html", {"request": request})


if mode == "offline":
    # 정적 파일 경로 설정
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/docs", include_in_schema=False)
    def custom_swagger_ui():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            # swagger_ui_preset_url="/static/swagger-ui-standalone-preset.js",
        )
