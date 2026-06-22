
import json

from fastapi import WebSocket, WebSocketDisconnect

from backend.api.ws.connection_manager import manager
from backend.core.settings import settings
from backend.crud.auth.main import main_crud
from backend.crud.auth.user import user_crud
from backend.deps.database import AsyncSessionLocal
from backend.models.auth.user import User
from backend.utils.ip_address import get_ip
from backend.utils.jwt_token import decode_access_token


async def _authenticate_ws(websocket: WebSocket, token: str) -> User | None:
    try:
        payload = decode_access_token(token)
        session_token = payload.get('session')
        if not session_token:
            return None

        # check if token ip and sender ip matches
        if settings.ip_check_enabled:
            request_ip = get_ip(websocket)
            token_ip = payload.get('ip_address')
            if token_ip and request_ip and request_ip != token_ip:
                return None

        async with AsyncSessionLocal() as db:
            main_session = await main_crud.get_by_session(db, session=session_token)
            if not main_session or not main_session.user_id:
                return None
            return await user_crud.get(db=db, id=main_session.user_id)
    except Exception:
        return None


async def websocket_endpoint(websocket: WebSocket, token: str):
    user = await _authenticate_ws(websocket, token)
    if user is None:
        await websocket.accept()
        await websocket.send_text(json.dumps({
            'type': 'error',
            'text': 'Unauthorized',
        }))
        await websocket.close(code=4401)
        return

    await manager.connect(user.id, user.username, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            # 🏓
            if data.get('type') == 'ping':
                await websocket.send_text(json.dumps({'type': 'pong'}))
                continue

            if data.get('type') == 'message':
                chat_id = data.get('chat_id')
                text = (data.get('text') or '').strip()
                if not chat_id or not text:
                    continue

                async with AsyncSessionLocal() as db:
                    from backend.services.chat.send_message import send_message
                    await send_message(
                        db=db,
                        current_user=user,
                        chat_id=int(chat_id),
                        text=text,
                    )
    except WebSocketDisconnect:
        manager.disconnect(user.id)
        await manager.broadcast_presence()

