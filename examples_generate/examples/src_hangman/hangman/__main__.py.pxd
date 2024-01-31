import cython


cdef class HangmanGame:
    cdef public list words
    cdef public str word_to_guess
    cdef public list guessed_letters
    cdef public int attempts

    def __init__(self)

    cdef choose_word(self)

    def display_word(self)

    def make_guess(self, str)