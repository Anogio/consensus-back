import uuid
import random
from collections import defaultdict
from typing import Union, Tuple

from src.state_store import StateStore
from src.domain.entities import Round, PlayerName, GuessList, GameError, RoundResult
from src.domain.constants import THEME_WORDS


def compute_round_result(guesses_by_player: dict[PlayerName, GuessList]) -> RoundResult:
    word_counts = defaultdict(int)
    for guess_list in guesses_by_player.values():
        for word in guess_list.words:
            word_counts[word] += 1
    word_point_values = {k: v - 1 for k, v in word_counts.items()}
    score_by_player_name = {}
    for player_name, guess_list in guesses_by_player.items():
        player_score = sum(word_point_values[word] for word in guess_list.words)
        score_by_player_name[player_name] = player_score
    return RoundResult(
        value_by_word=word_point_values, score_by_player_name=score_by_player_name
    )


class Game:
    """
    Holds the full game logic: theme selection, guess storage, scoring
    """

    def __init__(self, state: StateStore):
        self.state = state

    @property
    def has_ongoing_round(self) -> bool:
        latest_round, result = self.get_game_state()
        return latest_round is not None and result is None

    def start_new_round(self):
        latest_round = self.state.get_latest_round()
        if (
            latest_round is not None
            and self.state.get_round_result(latest_round.round_id) is None
        ):
            raise GameError("Must complete current round before starting a new one")

        self.state.add_round(
            Round(
                round_id=uuid.uuid4(),
                theme_word=random.choice(THEME_WORDS),
            )
        )

    def set_guesses(self, player_name: PlayerName, guess_list: GuessList):
        latest_round = self.state.get_latest_round()
        if (
            latest_round is None
            or self.state.get_round_result(latest_round.round_id) is not None
        ):
            raise GameError("Cannot set guesses as there is no ongoing round")

        self.state.set_player_guesses(
            round_id=latest_round.round_id,
            player_name=player_name,
            guess_list=guess_list,
        )

    def complete_current_round(self):
        latest_round = self.state.get_latest_round()
        if (
            latest_round is None
            or self.state.get_round_result(latest_round.round_id) is not None
        ):
            raise GameError("Cannot complete round as there is no ongoing round")

        guesses_by_player = self.state.get_all_guesses_for_round(latest_round.round_id)
        result = compute_round_result(guesses_by_player)
        self.state.add_round_result(round_id=latest_round.round_id, result=result)

    def get_game_state(self) -> Tuple[Union[Round, None], Union[RoundResult, None]]:
        latest_round = self.state.get_latest_round()
        if latest_round is None:
            return None, None
        latest_round_result = self.state.get_round_result(latest_round.round_id)
        return latest_round, latest_round_result
