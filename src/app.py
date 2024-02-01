from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import datetime as dt
from fastapi.middleware.cors import CORSMiddleware

from src.connectivity import WebsocketConnectionPool
from src.domain.entities import GameError
from src.game_runer import GameRunner

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://consensus.anog.fr",
    "https://www.consensus.anog.fr",
    "https://consensus-front.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

websocket_connection_pool = WebsocketConnectionPool()
runner = GameRunner(connection_pool=websocket_connection_pool)


@app.on_event("startup")
async def app_startup():
    asyncio.create_task(runner.run_game_loop_forever())


@app.get("/")
def healthcheck():
    return {"status": "ok"}


@app.post("/switch")
def switch():
    """
    Debug endpoint to end the current round or start a new round immediately
    """
    runner.next_switch = dt.datetime.now(dt.timezone.utc)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main endpoint for client connectivity
    Updates the connection pool, sends player info and receives player guesses
    Game state is provided once, then broadcasted directly from the game runner
    """
    player_name = websocket.query_params["player_name"]
    print(f"Connected player: {player_name}")

    await websocket_connection_pool.connect(websocket)
    await websocket_connection_pool.broadcast(
        {
            "type": "players_info",
            "data": {"n_players": len(websocket_connection_pool.active_connections)},
        }
    )
    try:
        await runner.personal_send_game_state(websocket=websocket)
        while True:
            data = await websocket.receive_json()
            try:
                print("Received data: ", data)
                # Only one type of event: set the guesses
                runner.set_guesses(player_name=player_name, guesses=data["words"])
            except GameError as e:
                await websocket.send_json(
                    {"type": "error", "data": {"message": str(e)}}
                )
    except WebSocketDisconnect:
        websocket_connection_pool.disconnect(websocket)
        await websocket_connection_pool.broadcast(
            {
                "type": "players_info",
                "data": {
                    "n_players": len(websocket_connection_pool.active_connections)
                },
            }
        )
