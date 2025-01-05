from talon import Module, actions, imgui
from typing import List

last_phrase = ""
phrase_numbering = ""
words = []
corrections = []
correction_texts = []

def compute_biggest_prefix_size_at_the_end_of_text(text, prefix):
    for i in range(len(prefix), 0, -1):
        if text.endswith(prefix[:i]):
            return i
    return 0

class Casing:
    UPPERCASE = 1
    LOWERCASE = 2
    CAPITALIZED = 3
    OTHER = 4
    def __init__(self, word: str):
        self.word = word
        if word.islower():
            self.casing = Casing.LOWERCASE
        elif word.isupper():
            if len(word) == 1:
                self.casing = Casing.CAPITALIZED
            else:
                self.casing = Casing.UPPERCASE
        elif word[0].isupper():
            self.casing = Casing.CAPITALIZED
        else:
            self.casing = Casing.OTHER
    
    def convert(self, word: str):
        if self.casing == Casing.UPPERCASE:
            return word.upper()
        elif self.casing == Casing.LOWERCASE:
            return word.lower()
        elif self.casing == Casing.CAPITALIZED:
            return word.capitalize()
        else:
            return word


module = Module()
@module.action_class
class Actions:
    def correction_chicken_update_last_phrase(phrase: str):
        """Update the last phrase dictated"""
        global last_phrase, phrase_numbering, words, corrections, correction_texts
        if phrase != last_phrase:
            actions.user.correction_chicken_set_last_phrase(phrase)
            words = []
            last_phrase = phrase
            phrase_numbering = ""
            number = 1
            word = ""
            for index, character in enumerate(phrase):
                if character == " " or index == len(phrase) - 1:
                    if index == len(phrase) - 1:
                        word += character
                    words.append(word)
                    if number == 1:
                        phrase_numbering += " "
                    phrase_numbering += f"({number}"
                    homophones = actions.user.correction_chicken_get_homophones(word)
                    if len(homophones) == 2:
                        phrase_numbering += "!"
                    elif len(homophones) > 2:
                        phrase_numbering += "*"
                    phrase_numbering += f") {word} "
                    word = ""

                    number += 1
                else:
                    word += character
            corrections = actions.user.correction_chicken_compute_corrections_for_phrase(phrase)
            correction_texts = [correction.original + " -> " + correction.replacement for correction in corrections]

    def correction_chicken_replace_text(replacement: str):
        """Replace the phrase with the specified text"""
        global last_phrase
        for _ in range(len(last_phrase)):
            actions.edit.delete()
        actions.insert(replacement)
        actions.user.correction_chicken_update_last_phrase(replacement)
        
    def correction_chicken_replace_text_with_words(words: List[str]):
        """Update the last phrase dictated with the specified words"""
        global last_phrase
        actions.user.correction_chicken_replace_text(" ".join(words))

    def correction_chicken_replace_word_with_same_casing(index: str, replacement: str):
        """Replace the specified word with the specified replacement using the same casing"""
        global words
        word = words[index - 1]
        casing = Casing(word)
        words[index - 1] = casing.convert(replacement)
        actions.user.correction_chicken_replace_text_with_words(words)

    def correction_chicken_remove_characters_from_word(word_number: int, characters: int):
        """Remove the specified number of characters from the specified word"""
        global words
        word = words[word_number - 1]
        new_word = word[:-characters]
        words[word_number - 1] = new_word
        actions.user.correction_chicken_replace_text_with_words(words)
    
    def correction_chicken_add_characters_to_word_ending(word_number: int, text: str):
        """Add the specified text to the end of the last word"""
        global words
        words[word_number - 1] += text
        actions.user.correction_chicken_replace_text_with_words(words)

    def correction_chicken_toggle():
        """Toggles the correction chicken GUI"""
        if gui.showing:
            gui.hide()
        else:
            gui.show()
    
    def correction_chicken_remove_word(word_number: int):
        """Remove the specified word"""
        global words
        words.pop(word_number - 1)
        actions.user.correction_chicken_replace_text_with_words(words)

    def correction_chicken_get_last_word_with_homophones_number():
        """Get the number of the last word that is a homophone"""
        global words
        for index in range(len(words) - 1, -1, -1):
            word = words[index]
            if actions.user.correction_chicken_get_homophones(word):
                return index + 1
        return -1

    def correction_chicken_homophones_advance_word(word_number: int=0):
        """Advance the word to the next homophone"""
        if word_number == 0:
            word_number = actions.user.correction_chicken_get_last_word_with_homophones_number()
            if word_number == -1:
                return

        global words
        word = words[word_number - 1].lower()
        homophones = actions.user.correction_chicken_get_homophones(word)
        if homophones:
            index = homophones.index(word)
            index = (index + 1) % len(homophones)
            actions.user.correction_chicken_replace_word_with_same_casing(word_number, homophones[index])
        
    def correction_chicken_get_homophones_other_than_word(word: str):
        """Get the homophones for the specified word other than the word itself"""
        homophones = actions.user.correction_chicken_get_homophones(word)
        homophones.remove(word.lower())
        return homophones

    def correction_chicken_change_word_to_homophone_with_most_occurrences_of_character(word_number: int, character: str):
        """Change the word to the homophone with the most occurrences of the specified character"""
        global words
        word = words[word_number - 1]
        homophones = actions.user.correction_chicken_get_homophones_other_than_word(word)
        if homophones:
            occurrences = [homophone.count(character) for homophone in homophones]
            index = occurrences.index(max(occurrences))
            actions.user.correction_chicken_replace_word_with_same_casing(word_number, homophones[index])

    def correction_chicken_change_word_to_homophone_containing_characters(word_number: int, characters: List[str]):
        """Change the word to the homophone containing the specified characters"""
        global words
        word = words[word_number - 1]
        homophones = actions.user.correction_chicken_get_homophones_other_than_word(word)
        sub_string = "".join(characters)
        if homophones:
            for homophone in homophones:
                if sub_string in homophone:
                    actions.user.correction_chicken_replace_word_with_same_casing(word_number, homophone)
                    break

    def correction_chicken_perform_correction(correction_number: int):
        """Perform the specified correction"""
        global corrections
        correction = corrections[correction_number - 1]
        replacement = correction.replacement
        index = correction.starting_index
        new_text = last_phrase[:index] + replacement
        post_index = index + len(correction.original)
        if post_index < len(last_phrase):
            new_text += last_phrase[index + len(correction.original):]
        actions.user.correction_chicken_replace_text(new_text)
    
    def correction_chicken_add_missing_text_to_the_end(word_number: int, text: str):
        """Make the ending of the word match the text preserving already present characters"""
        global words
        word = words[word_number - 1]
        biggest_prefix_size = compute_biggest_prefix_size_at_the_end_of_text(word, text)
        words[word_number - 1] += text[biggest_prefix_size:]
        actions.user.correction_chicken_replace_text_with_words(words)
    
@imgui.open(y=0)
def gui(gui: imgui.GUI):
    global last_phrase, phrase_numbering
    gui.text(phrase_numbering)
    gui.line()
    for index, correction_text in enumerate(correction_texts):
        gui.text(f"{index + 1}. {correction_text}")