import dataclasses
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
        words_processed = [word.lower().strip() for word in words]
        if words_processed != words:
            raise GameError(
                "Technical error: all guesses shoud be sent lowercase with no trailing or leading spaces"
            )
        if len(words_processed) > N_GUESSES:
            raise GameError("Too many guesses")
        if len(set(words_processed)) != len(words_processed):
            raise GameError("Some words are identical")
        self.words = words_processed

    def __repr__(self):
        return f"GuessList({self.words})"


@dataclasses.dataclass
class GameState:
    rounds: list[Round]
    result_by_round: dict[RoundId, RoundResult]
    guesses_by_round_and_player_name: dict[RoundId, dict[PlayerName, GuessList]]
