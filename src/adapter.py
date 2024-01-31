from src.entities import PlayerName, RoundId, Round, RoundResult, GuessList, GameState

from typing import Union


class StateManager:
    max_rounds_stored = 10

    def __init__(self):
        self.state = GameState(
            rounds=[], result_by_round={}, guesses_by_round_and_player_name={}
        )

    def cleanup(self) -> None:
        """
        Since we store the rounds in memory, only keep the last few rounds
        """
        if len(self.state.rounds) > self.max_rounds_stored:
            self.state.rounds = self.state.rounds[-self.max_rounds_stored :]

        allowed_round_ids = set(r.round_id for r in self.state.rounds)
        self.state.result_by_round = {
            round_id: result
            for round_id, result in self.state.result_by_round.items()
            if round_id in allowed_round_ids
        }
        self.state.guesses_by_round_and_player_name = {
            round_id: guesses_dict
            for round_id, guesses_dict in self.state.guesses_by_round_and_player_name.items()
            if round_id in allowed_round_ids
        }

    def get_latest_round(self) -> Union[Round, None]:
        if len(self.state.rounds) == 0:
            return None
        return self.state.rounds[-1]

    def add_round(self, round_to_add: Round) -> None:
        self.state.rounds.append(round_to_add)
        self.state.guesses_by_round_and_player_name[round_to_add.round_id] = {}

        self.cleanup()

    def get_round_result(self, round_id: RoundId) -> RoundResult:
        return self.state.result_by_round.get(round_id)

    def add_round_result(self, round_id: RoundId, result: RoundResult) -> None:
        self.state.result_by_round[round_id] = result

    def get_player_guesses(
        self, round_id: RoundId, player_name: PlayerName
    ) -> GuessList:
        if player_name in self.state.guesses_by_round_and_player_name[round_id]:
            return self.state.guesses_by_round_and_player_name[round_id][player_name]
        return GuessList([])

    def set_player_guesses(
        self, round_id: RoundId, player_name: PlayerName, guess_list: GuessList
    ) -> None:
        self.state.guesses_by_round_and_player_name[round_id][player_name] = guess_list

    def get_all_guesses_for_round(
        self, round_id: RoundId
    ) -> dict[PlayerName, GuessList]:
        return self.state.guesses_by_round_and_player_name[round_id]
