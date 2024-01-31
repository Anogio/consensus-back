from src.game import Game
from src.adapter import StateManager
from src.entities import GameError, GuessList, Round, RoundResult, RoundId

import pytest


def test_game_base_mechanics():
    """
    We can start a round, complete it and start a new one
    We cannot start multiple rounds at once, or end already completed rounds
    """
    state = StateManager()
    game = Game(state)

    assert game.get_game_state() == (None, None)
    assert not game.has_ongoing_round

    with pytest.raises(GameError, match="Cannot complete round"):
        game.complete_current_round()

    with pytest.raises(GameError, match="Cannot set guesses"):
        game.set_guesses("Anog", GuessList(["Test"]))

    game.start_new_round()
    with pytest.raises(GameError, match="Must complete current round"):
        game.start_new_round()

    assert game.has_ongoing_round
    round, result = game.get_game_state()
    assert result is None
    assert isinstance(round.round_id, RoundId)
    assert isinstance(round.theme_word, str)

    game.complete_current_round()
    assert not game.has_ongoing_round
    round_after_complete, result = game.get_game_state()
    assert round == round_after_complete
    assert result == RoundResult(value_by_word={}, score_by_player_name={})

    with pytest.raises(GameError, match="Cannot complete round"):
        game.complete_current_round()
    game.start_new_round()
    assert game.has_ongoing_round
    round, result = game.get_game_state()
    assert result is None
    assert isinstance(round.round_id, RoundId)
    assert isinstance(round.theme_word, str)


def test_play_round():
    state = StateManager()
    game = Game(state)

    game.start_new_round()
    game.set_guesses(player_name="Anog", guess_list=GuessList(["Bonjour", "Test"]))
    game.complete_current_round()
    round, result = game.get_game_state()

    assert isinstance(round, Round)
    assert result == RoundResult(
        value_by_word={"Bonjour": 0, "Test": 0}, score_by_player_name={"Anog": 0}
    )


def test_compute_score_3_players():
    state = StateManager()
    game = Game(state)

    game.start_new_round()
    game.set_guesses(player_name="Anog1", guess_list=GuessList(["Everyone", "JustMe"]))
    game.set_guesses(player_name="Anog2", guess_list=GuessList(["Everyone", "2People"]))
    game.set_guesses(
        player_name="Anog3",
        guess_list=GuessList(["Everyone", "2People", "AnotherJustMe"]),
    )
    game.complete_current_round()
    round, result = game.get_game_state()
    assert isinstance(round, Round)
    assert result == RoundResult(
        value_by_word={"Everyone": 2, "JustMe": 0, "2People": 1, "AnotherJustMe": 0},
        score_by_player_name={"Anog1": 2, "Anog2": 3, "Anog3": 3},
    )


def test_replace_guesses():
    state = StateManager()
    game = Game(state)

    game.start_new_round()
    game.set_guesses(
        player_name="Anog1", guess_list=GuessList(["Everyone", "ToChange"])
    )
    game.set_guesses(player_name="Anog2", guess_list=GuessList(["JustMe", "ToChange"]))
    game.set_guesses(player_name="Anog2", guess_list=GuessList(["Everyone", "JustMe2"]))
    game.complete_current_round()
    round, result = game.get_game_state()
    assert isinstance(round, Round)
    assert result == RoundResult(
        value_by_word={"Everyone": 1, "ToChange": 0, "JustMe2": 0},
        score_by_player_name={"Anog1": 1, "Anog2": 1},
    )
