import pytest
from src.entities import GuessList, GameError
from src.constants import N_GUESSES


def test_guess_list_rejects_too_many_guesses():
    with pytest.raises(GameError, match="Too many guesses"):
        GuessList(words=[f"Word{i}" for i in range(N_GUESSES + 1)])


def test_guess_list_rejects_duplicate_guesses():
    with pytest.raises(GameError, match="Some words are identical"):
        GuessList(words=["CaseInsensitive", "caSeinsensiTive"])
