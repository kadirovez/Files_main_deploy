
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.router import api_router
from backend.api.ws.ws_endpoints import websocket_endpoint
from backend.core.database import close_db, init_db
from backend.core.settings import settings

FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,
    version=settings.app_version,
    docs_url='/docs' if settings.debug else None,
    openapi_url='/openapi.json' if settings.debug else None,
    lifespan=lifespan,
)

app.include_router(api_router, prefix='/api/v1')
app.mount('/static', StaticFiles(directory=str(FRONTEND_DIR / 'static')), name='static')


@app.get('/')
async def index():
    return FileResponse(str(FRONTEND_DIR / 'templates' / 'index.html'))


@app.get('/chat')
async def chat_page():
    return FileResponse(str(FRONTEND_DIR / 'templates' / 'chat.html'))


@app.websocket('/ws')
async def ws_route(websocket: WebSocket, token: str):
    await websocket_endpoint(websocket, token)
