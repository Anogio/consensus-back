from starlette.websockets import WebSocket
from uvicorn.protocols.utils import ClientDisconnected


class WebsocketConnectionPool:
    """
    Maintains a list of connected users to enable broadcasting game state and other info
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await self.send_personal_message(message, connection)
