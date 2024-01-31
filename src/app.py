from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import datetime as dt
from fastapi.middleware.cors import CORSMiddleware


from src.adapter import StateManager
from src.entities import PlayerName, GuessList, GameError
from src.game import Game
from src.constants import ROUND_DURATION_SECONDS, INTER_ROUND_DURATION_SECONDS

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_personal_message(message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


class GameRunner:
    def __init__(self, manager: ConnectionManager):
        self.game = Game(state=StateManager())
        self.connection_manager = manager
        self.next_switch = dt.datetime.now()

    async def run_game_loop(self):
        print("Initializing game loop")
        while True:
            await asyncio.sleep(0.1)
            if dt.datetime.now() <= self.next_switch:
                continue

            if self.game.has_ongoing_round:
                # A round is ongoing and has ended
                print(
                    f"Completed round for word {self.game.get_game_state()[0].theme_word}"
                )
                self.game.complete_current_round()
                self.next_switch = dt.datetime.now() + dt.timedelta(
                    seconds=INTER_ROUND_DURATION_SECONDS
                )
            else:
                # Time to start a new round
                self.game.start_new_round()
                print(
                    f"Started round for word {self.game.get_game_state()[0].theme_word}"
                )
                self.next_switch = dt.datetime.now() + dt.timedelta(
                    seconds=ROUND_DURATION_SECONDS
                )

            await self.broadcast_game_state()

    @property
    def game_state_message(self) -> dict:
        latest_round, result = self.game.get_game_state()
        if latest_round is None:
            raise ValueError(
                "Unexpected: round should never be None after initialization"
            )

        if result is None:
            return {
                "type": "game_state",
                "data": {
                    "round": {
                        "theme_word": latest_round.theme_word,
                        "is_completed": False,
                    },
                    "round_end": self.next_switch.isoformat(),
                },
            }
        return {
            "type": "game_state",
            "data": {
                "round": {"theme_word": latest_round.theme_word, "is_completed": True},
                "next_round_start": self.next_switch.isoformat(),
                "result": {
                    "ranked_value_by_word": [
                        {"word": item[0], "value": item[1]}
                        for item in sorted(
                            result.value_by_word.items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    ],
                    "ranked_score_by_player_name": [
                        {"player_name": item[0], "score": item[1]}
                        for item in sorted(
                            result.score_by_player_name.items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    ],
                },
            },
        }

    async def broadcast_game_state(self):
        await self.connection_manager.broadcast(self.game_state_message)

    async def personal_send_game_state(self, websocket: WebSocket):
        await self.connection_manager.send_personal_message(
            self.game_state_message, websocket
        )

    def set_guesses(self, player_name: PlayerName, guesses: list[str]):
        self.game.set_guesses(player_name=player_name, guess_list=GuessList(guesses))


connection_manager = ConnectionManager()
runner = GameRunner(manager=connection_manager)


@app.on_event("startup")
async def app_startup():
    asyncio.create_task(runner.run_game_loop())


@app.get("/")
def healthcheck():
    return {"status": "ok"}


@app.post("/switch")
def switch():
    runner.next_switch = dt.datetime.now()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    player_name = websocket.query_params["player_name"]
    print(f"Connected player: {player_name}")

    await connection_manager.connect(websocket)
    await connection_manager.broadcast(
        {
            "type": "players_info",
            "data": {"n_players": len(connection_manager.active_connections)},
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
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast(
            {
                "type": "players_info",
                "data": {"n_players": len(connection_manager.active_connections)},
            }
        )
