import pytest

from .__main__ import HangmanGame


@pytest.fixture
def new_game():
    return HangmanGame()


def test_choose_word(new_game):
    new_game.choose_word()
    assert new_game.word_to_guess in new_game.words


def test_display_word(new_game):
    new_game.word_to_guess = "programming"
    new_game.guessed_letters = ["p", "r", "o", "g"]
    assert new_game.display_word() == "progr_____g"


def test_make_guess_correct(new_game):
    new_game.word_to_guess = "hangman"
    result = new_game.make_guess("a")
    assert result is None  # Correct guess should return None (no message)


def test_make_guess_incorrect(new_game):
    new_game.word_to_guess = "python"
    result = new_game.make_guess("z")
    assert result == "Incorrect guess!"


def test_make_guess_already_guessed(new_game):
    new_game.word_to_guess = "challenge"
    new_game.guessed_letters = ["c", "h", "a"]
    result = new_game.make_guess("a")
    assert result == "You've already guessed that letter."


def test_make_guess_game_over(new_game):
    new_game.word_to_guess = "hangman"
    new_game.attempts = 1
    result = new_game.make_guess("z")
    assert "Game over" in result


def test_make_guess_win(new_game):
    new_game.word_to_guess = "python"
    new_game.guessed_letters = ["p", "y", "t", "h", "o"]
    result = new_game.make_guess("n")
    assert "Congratulations" in result


if __name__ == "__main__":
    pytest.main()
