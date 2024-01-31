from src.entities import PlayerName, RoundId, Round, RoundResult, GuessList, GameState


class StateManager:
    def __init__(self):
        self.state = GameState(
            rounds=[], result_by_round={}, guesses_by_round_and_player_name={}
        )

    def get_latest_round(self) -> Round | None:
        if len(self.state.rounds) == 0:
            return None
        return self.state.rounds[-1]

    def add_round(self, round: Round) -> None:
        self.state.rounds.append(round)
        self.state.guesses_by_round_and_player_name[round.round_id] = {}

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
