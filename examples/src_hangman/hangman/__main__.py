import random


class HangmanGame:
    def __init__(self):
        self.words = ["python", "hangman", "programming", "game", "challenge"]
        self.word_to_guess = ""
        self.guessed_letters = []
        self.attempts = 6

    def choose_word(self):
        # A method to randomly choose a word from the list of words
        self.word_to_guess = random.choice(self.words)

    def display_word(self):
        # A method to display the word with correctly guessed letters and underscores for missing letters
        display = ""
        for letter in self.word_to_guess:
            if letter in self.guessed_letters:
                display += letter
            else:
                display += "_"
        return display

    def make_guess(self, guess):
        # A method to process a user's guess and update game state
        if len(guess) != 1 or not guess.isalpha():
            return "Please enter a single letter."

        guess = guess.lower()

        if guess in self.guessed_letters:
            return "You've already guessed that letter."

        self.guessed_letters.append(guess)

        if guess not in self.word_to_guess:
            self.attempts -= 1

            if self.attempts == 0:
                return "Game over! You've run out of attempts. The word was: " + self.word_to_guess
            else:
                return "Incorrect guess!"

        if "_" not in self.display_word():
            return "Congratulations! You've won. The word was: " + self.word_to_guess


def hangman_ui():
    game = HangmanGame()
    game.choose_word()
    print("Welcome to Hangman!")

    while True:
        print("\nAttempts left:", game.attempts)
        print("Word:", game.display_word())

        guess = input("Guess a letter: ")
        result = game.make_guess(guess)

        if result:
            print(result)
            if "Congratulations" in result or "Game over" in result:
                break


if __name__ == "__main__":
    hangman_ui()
