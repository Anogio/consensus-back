import asyncio
import datetime as dt

from starlette.websockets import WebSocket

from src.state_store import StateStore
from src.connectivity import WebsocketConnectionPool
from src.domain.constants import INTER_ROUND_DURATION_SECONDS, ROUND_DURATION_SECONDS
from src.domain.entities import PlayerName, GuessList
from src.domain.game import Game


class GameRunner:
    """
    Runs the game loop that starts and completes rounds, and broadcasts game state
    """

    def __init__(self, connection_pool: WebsocketConnectionPool):
        self.game = Game(state=StateStore())
        self.websocket_connection_pool = connection_pool

        self.next_switch = dt.datetime.now(dt.timezone.utc)

    async def run_game_loop_forever(self):
        while True:
            try:
                await self.run_game_loop()
            except Exception as e:
                print("Loop failed with exception: ", repr(e))

    async def run_game_loop(self):
        print("Initializing game loop")
        while True:
            await asyncio.sleep(0.1)
            if dt.datetime.now(dt.timezone.utc) <= self.next_switch:
                continue

            if self.game.has_ongoing_round:
                # A round is ongoing and has ended
                print(
                    f"Completed round for word {self.game.get_game_state()[0].theme_word}"
                )
                self.game.complete_current_round()
                self.next_switch = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
                    seconds=INTER_ROUND_DURATION_SECONDS
                )
            else:
                # Time to start a new round
                self.game.start_new_round()
                print(
                    f"Started round for word {self.game.get_game_state()[0].theme_word}"
                )
                self.next_switch = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
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
        await self.websocket_connection_pool.broadcast(self.game_state_message)

    async def personal_send_game_state(self, websocket: WebSocket):
        await self.websocket_connection_pool.send_personal_message(
            self.game_state_message, websocket
        )

    def set_guesses(self, player_name: PlayerName, guesses: list[str]):
        self.game.set_guesses(player_name=player_name, guess_list=GuessList(guesses))
