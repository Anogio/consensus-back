import dataclasses
import datetime as dt
from uuid import UUID

from src.constants import N_GUESSES

PlayerName = str
RoundId = UUID


class GameError(Exception):
    pass


@dataclasses.dataclass
class Round:
    round_id: RoundId
    theme_word: str


@dataclasses.dataclass
class RoundResult:
    score_by_player_name: dict[str, int]
    value_by_word: dict[str, int]


class GuessList:
    """A list of 0 to N_GUESSES distinct words"""

    def __init__(self, words: list[str]):
        words_processed = [word.lower() for word in words]
        if len(words_processed) > N_GUESSES:
            raise GameError("Too many guesses")
        if len(set(words_processed)) != len(words):
            raise GameError("Some words are identical")
        self.words = words_processed


@dataclasses.dataclass
class GameState:
    rounds: list[Round]
    result_by_round: dict[RoundId, RoundResult]
    guesses_by_round_and_player_name: dict[RoundId, dict[PlayerName, GuessList]]
