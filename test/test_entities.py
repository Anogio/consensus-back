import pytest
from src.domain.entities import GuessList, GameError
from src.domain.constants import N_GUESSES


def test_guess_list_rejects_too_many_guesses():
    with pytest.raises(GameError, match="Too many guesses"):
        GuessList(words=[f"word{i}" for i in range(N_GUESSES + 1)])


def test_guess_list_rejects_duplicate_guesses():
    with pytest.raises(GameError, match="Some words are identical"):
        GuessList(words=["word", "word"])


def test_guess_list_enforces_lowercase_stripped():
    with pytest.raises(GameError, match="Technical error"):
        GuessList(words=["Word"])

    with pytest.raises(GameError, match="Technical error"):
        GuessList(words=[" word"])

    with pytest.raises(GameError, match="Technical error"):
        GuessList(words=["word "])
