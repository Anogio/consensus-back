from src.domain.game import Game
from src.state_store import StateStore
from src.domain.entities import GameError, GuessList, Round, RoundResult, RoundId

import pytest


def test_game_base_mechanics():
    """
    We can start a round, complete it and start a new one
    We cannot start multiple rounds at once, or end already completed rounds
    """
    state = StateStore()
    game = Game(state)

    assert game.get_game_state() == (None, None)
    assert not game.has_ongoing_round

    with pytest.raises(GameError, match="Cannot complete round"):
        game.complete_current_round()

    with pytest.raises(GameError, match="Cannot set guesses"):
        game.set_guesses("Anog", GuessList(["test"]))

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
    state = StateStore()
    game = Game(state)

    game.start_new_round()
    game.set_guesses(player_name="Anog", guess_list=GuessList(["bonjour", "test"]))
    game.complete_current_round()
    round, result = game.get_game_state()

    assert isinstance(round, Round)
    assert result == RoundResult(
        value_by_word={"bonjour": 0, "test": 0}, score_by_player_name={"Anog": 0}
    )


def test_compute_score_3_players():
    state = StateStore()
    game = Game(state)

    game.start_new_round()
    game.set_guesses(player_name="Anog1", guess_list=GuessList(["everyone", "justme"]))
    game.set_guesses(player_name="Anog2", guess_list=GuessList(["everyone", "2people"]))
    game.set_guesses(
        player_name="Anog3",
        guess_list=GuessList(["everyone", "2people", "anotherjustme"]),
    )
    game.complete_current_round()
    round, result = game.get_game_state()
    assert isinstance(round, Round)
    assert result == RoundResult(
        value_by_word={"everyone": 2, "justme": 0, "2people": 1, "anotherjustme": 0},
        score_by_player_name={"Anog1": 2, "Anog2": 3, "Anog3": 3},
    )


def test_replace_guesses():
    state = StateStore()
    game = Game(state)

    game.start_new_round()
    game.set_guesses(
        player_name="Anog1", guess_list=GuessList(["everyone", "tochange"])
    )
    game.set_guesses(player_name="Anog2", guess_list=GuessList(["justme", "tochange"]))
    game.set_guesses(player_name="Anog2", guess_list=GuessList(["everyone", "justme2"]))
    game.complete_current_round()
    round, result = game.get_game_state()
    assert isinstance(round, Round)
    assert result == RoundResult(
        value_by_word={"everyone": 1, "tochange": 0, "justme2": 0},
        score_by_player_name={"Anog1": 1, "Anog2": 1},
    )
