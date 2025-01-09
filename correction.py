from talon import Module, actions, imgui, Context
from typing import List, Union, Tuple

last_phrase = ""
phrase_numbering = ""
tokens = None
corrections = []
correction_texts = []
replacement = ""
current_editing_word_number_range = None

def is_token_over(token, next_character):
    """A new token is encountered if transitioning from alphabetic to non alphabetic or from non alphabetic to alphabetic as well as when encountering a space"""
    if not token:
        return False
    last_character = token[-1]
    return last_character.isalpha() != next_character.isalpha() or next_character.isspace() or (last_character.islower() and next_character.isupper())

class Tokens:
    def _add_token(self):
        self.tokens.append(self.token)
        if len(self.tokens) > 1:
            self.spacing.append(self.spaces)
        if self.token[-1].isalpha():
            self.word_indexes.append(len(self.tokens) - 1)
        self.spaces = ""
        self.token = ""

    def __init__(self, text):
        self.tokens = []
        self.spacing = []
        self.word_indexes = []
        self.spaces = ""
        self.token = ""
        for character in text:
            if is_token_over(self.token, character):
                self._add_token()
            if character.isspace():
                self.spaces += character
            else:
                self.token += character
        if self.token:
            self._add_token()
        self.spacing.append(self.spaces)

    def get_token(self, index):
        return self.tokens[index]

    def get_size(self):
        return len(self.tokens)
    
    def get_text(self):
        return " ".join(self.tokens)

    def set_token(self, index: int, token: str):
        self.tokens[index] = token

    def get_tokens(self, start_index, end_index):
        return self.tokens[start_index:end_index]

    def set_tokens(self, start_index, end_index, tokens):
        self.tokens[start_index:end_index] = tokens

    def get_words(self):
        return [self.get_token(index) for index in self.word_indexes]

    def set_word(self, index, word):
        self.tokens[self.word_indexes[index]] = word

    def get_word(self, index):
        return self.tokens[self.word_indexes[index]]

    def get_word_index(self, index):
        return self.word_indexes[index]
    
    def remove_token(self, index):
        self.tokens.pop(index)

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        result = ""
        for i in range(len(self.tokens)):
            result += self.tokens[i] + self.spacing[i]
        return result

    def __eq__(self, value: object) -> bool:
        return self.tokens == value.tokens

def compute_casing_based_on_neighbors(last_casing, replacement_token, next_casing):
    if not last_casing and not next_casing:
        casing = Casing.from_word(replacement_token)
    elif not next_casing:
        casing = last_casing
    elif (not last_casing) or last_casing == next_casing:
        casing = next_casing
    elif last_casing < next_casing:
        casing = last_casing
    else:
        casing = next_casing
    return casing

def compute_first_alphabetic_index_and_casing(tokens: Tokens, start_index):
    for i in range(start_index, tokens.get_size()):
        if tokens.get_token(i).isalpha():
            return i, Casing.from_word(tokens.get_token(i))
    return None, None

def compute_last_alphabetic_index_and_casing(tokens: Tokens, end_index):
    for i in range(end_index, -1, -1):
        if tokens.get_token(i).isalpha():
            return i, Casing.from_word(tokens.get_token(i))
    return None, None

def compute_before_casing(tokens: Tokens, start_number):
    if start_number > 1:
        first_index, first_casing = compute_first_alphabetic_index_and_casing(tokens, start_number - 2)
        if first_index is not None and first_index + 1 < start_number:
            last_casing = first_casing
        else:
            last_casing = None
    else:
        last_casing = None
    return last_casing

def compute_after_casing(tokens: Tokens, end_number):
    if end_number < tokens.get_size():
        last_index, last_casing = compute_last_alphabetic_index_and_casing(tokens, end_number)
        if last_index is not None and last_index + 1 > end_number:
            after_casing = last_casing
        else:
            after_casing = None
    else:
        after_casing = None
    return after_casing

def create_tokens_with_matching_casing(replacement_tokens, relevant_tokens, last_casing, after_casing):
    next_index = 0
    new_tokens = []
    for index, replacement_token in enumerate(replacement_tokens):
        if index < len(relevant_tokens) and relevant_tokens[index].isalpha():
            casing = Casing.from_word(relevant_tokens[index])
        else:
            if next_index <= index:
                while (next_index < len(relevant_tokens) and not relevant_tokens[next_index].isalpha()) or next_index <= index:
                    next_index += 1
                if next_index < len(relevant_tokens):
                    next_casing = Casing.from_word(relevant_tokens[next_index])
            if next_index >= len(relevant_tokens):
                next_casing = after_casing
            casing = compute_casing_based_on_neighbors(last_casing, replacement_token, next_casing)
        converted_token = casing.convert(replacement_token)
        new_tokens.append(converted_token)
        last_casing = casing
    return new_tokens

def replace_tokens_with_matching_casing(tokens: Tokens, index_range, replacement: str):
    start_number, end_number = index_range
    relevant_tokens = tokens.get_tokens(start_number - 1, end_number)
    tokens_for_replacement = Tokens(replacement)
    replacement_tokens = tokens_for_replacement.get_tokens(0, tokens_for_replacement.get_size())
    last_casing = compute_before_casing(tokens, start_number)
    after_casing = compute_after_casing(tokens, end_number)
    new_tokens = create_tokens_with_matching_casing(replacement_tokens, relevant_tokens, last_casing, after_casing)
    tokens.set_tokens(start_number - 1, end_number, new_tokens)

def compute_biggest_prefix_size_at_the_end_of_text(text, prefix):
    for i in range(len(prefix), 0, -1):
        if text.endswith(prefix[:i]):
            return i
    return 0

class Casing:
    LOWERCASE = 1
    CAPITALIZED = 2
    UPPERCASE = 3
    OTHER = 4
    def __init__(self, casing: int):
        self.casing = casing

    @staticmethod
    def from_word(word: str):
        if word.islower():
            case = Casing.LOWERCASE
        elif word.isupper():
            if len(word) == 1:
                case = Casing.CAPITALIZED
            else:
                case = Casing.UPPERCASE
        elif word[0].isupper():
            case = Casing.CAPITALIZED
        else:
            case = Casing.OTHER
        return Casing(case)

    def convert(self, word: str):
        if self.casing == Casing.UPPERCASE:
            return word.upper()
        elif self.casing == Casing.LOWERCASE:
            return word.lower()
        elif self.casing == Casing.CAPITALIZED:
            return word.capitalize()
        else:
            return word

    def __eq__(self, value: object) -> bool:
        return self.casing == value.casing

    def __lt__(self, value: object) -> bool:
        return self.casing < value.casing

SPEAKABLE_CASINGS = {
    "LOWER": Casing.LOWERCASE,
    "CAPITALIZED": Casing.CAPITALIZED,
    "UPPER": Casing.UPPERCASE,
}

def apply_speakable_casing(spoken_form, target):
    case = SPEAKABLE_CASINGS[spoken_form]
    casing = Casing(case)
    return casing.convert(target)

module = Module()
module.list("correction_chicken_casing", desc="Casing options")
module.tag("correction_chicken_replacement", desc="Enables replacement commands for correction chicken")
module.tag("correction_chicken", desc="Activates correction chicken commands")
context = Context()
replacement_context = Context()
@module.action_class
class Actions:
    def correction_chicken_update_last_phrase(phrase: str):
        """Update the last phrase dictated"""
        global last_phrase, phrase_numbering, corrections, correction_texts, tokens
        if phrase != last_phrase:
            actions.user.correction_chicken_set_last_phrase(phrase)
            tokens = Tokens(phrase)
            last_phrase = phrase
            phrase_numbering = ""
            for i in range(tokens.get_size()):
                new_text = ""
                if i > 0:
                    new_text += " "
                new_text += f"({i + 1}"
                homophones = actions.user.correction_chicken_get_homophones(tokens.get_token(i))
                if len(homophones) == 2:
                    new_text += "!"
                elif len(homophones) > 2:
                    new_text += "*"
                new_text += f"){tokens.get_token(i)}"
                phrase_numbering += new_text
                
            corrections = actions.user.correction_chicken_compute_corrections_for_phrase(phrase)
            correction_texts = [correction.original + " -> " + correction.replacement for correction in corrections]

    def correction_chicken_set_last_phrase_to_selected_text():
        """Set the last phrase to the selected text"""
        selected_text = actions.user.correction_chicken_get_selected_text()
        actions.edit.right()
        actions.user.correction_chicken_update_last_phrase(selected_text)

    def correction_chicken_replace_text(replacement: str):
        """Replace the phrase with the specified text"""
        global last_phrase

        number_of_leading_spaces = 0
        while number_of_leading_spaces < len(last_phrase) and last_phrase[number_of_leading_spaces].isspace():
            number_of_leading_spaces += 1

        for _ in range(len(last_phrase) - number_of_leading_spaces):
            actions.edit.delete()
        actions.insert(replacement)
        actions.user.correction_chicken_update_last_phrase(replacement)

    def correction_chicken_replace_text_with_tokens():
        """Replace the phrase with the phrase resulting from the tokens tokens"""
        actions.user.correction_chicken_replace_text(str(tokens))

    def correction_chicken_replace_word_with_same_casing(index: str, replacement: str):
        """Replace the specified word with the specified replacement using the same casing"""
        global tokens
        word = tokens.get_token(index - 1)
        casing = Casing.from_word(word)
        tokens.set_token(index - 1, casing.convert(replacement))
        actions.user.correction_chicken_replace_text_with_tokens()

    def correction_chicken_replace_words_with_same_casing(index_range: List[int], replacement: str):
        """Replace the specified words with the specified replacement using the same casing"""
        global tokens
        replace_tokens_with_matching_casing(tokens, index_range, replacement)
        actions.user.correction_chicken_replace_text_with_tokens()

    def correction_chicken_remove_characters_from_word(word_number: int, characters: int):
        """Remove the specified number of characters from the specified word"""
        global tokens
        token = tokens.get_token(word_number - 1)
        new_token = token[:-characters]
        tokens.set_token(word_number - 1, new_token)
        actions.user.correction_chicken_replace_text_with_tokens()
       
    def correction_chicken_add_characters_to_word_ending(word_number: int, text: str):
        """Add the specified text to the end of the last word"""
        global tokens
        token = tokens.get_token(word_number - 1)
        new_token = token + text
        tokens.set_token(word_number - 1, new_token)
        actions.user.correction_chicken_replace_text_with_tokens()

    def correction_chicken_toggle():
        """Toggles correction chicken"""
        if gui.showing:
            context.tags = []
            gui.hide()
        else:
            context.tags = ["user.correction_chicken"]
            gui.show()
    
    def correction_chicken_remove_word(word_number: int):
        """Remove the specified word"""
        global tokens
        tokens.remove_token(word_number - 1)
        actions.user.correction_chicken_replace_text_with_tokens()

    def correction_chicken_activate_replacement_context():
        """Activates the replacement context"""
        replacement_context.tags = ["user.correction_chicken_replacement"]

    def correction_chicken_deactivate_replacement_context():
        """Deactivates the replacement context"""
        replacement_context.tags = []

    def correction_chicken_set_current_number_range(range: Union[int, Tuple[int, int]]):
        """Set the current number range"""
        global current_editing_word_number_range
        current_editing_word_number_range = range
        actions.user.correction_chicken_activate_replacement_context()

    def correction_chicken_spell_out_alternative_for_word(characters: List[str], word_number: int=None):
        """Spell out the alternative for the specified word"""
        global current_editing_word_number_range, replacement
        if word_number is not None:
            actions.user.correction_chicken_set_current_number_range(word_number)
        replacement = "".join(characters)
    
    def correction_chicken_set_replacement(new_replacement: str):
        """Set the replacement"""
        global replacement
        replacement = new_replacement

    def correction_chicken_choose_word_for_replacement(word_number: int):
        """Update the current word for replacement"""
        global current_editing_word_number_range
        actions.user.correction_chicken_set_current_number_range(word_number)

    def fire_chicken_choosing_range_for_replacement(start_word_number: int, end_word_number: int):
        """Choose the range of words for replacement"""
        global current_editing_word_number_range
        actions.user.correction_chicken_set_current_number_range((start_word_number, end_word_number))

    def correction_chicken_make_replacement():
        """Make the replacement for the current word"""
        global current_editing_word_number_range, replacement
        if current_editing_word_number_range is not None and replacement:
            if type(current_editing_word_number_range) == int:
                actions.user.correction_chicken_replace_word_with_same_casing(current_editing_word_number_range, replacement)
            else:
                actions.user.correction_chicken_replace_words_with_same_casing(current_editing_word_number_range, replacement)
            current_editing_word_number_range = None
            replacement = ""
            actions.user.correction_chicken_deactivate_replacement_context()

    def correction_chickens_save_replacement_as_correction_rule():
        """Saves the current replacement as a correction rule"""
        global current_editing_word_number_range, replacement, tokens
        if current_editing_word_number_range is not None and replacement:
            if type(current_editing_word_number_range) == int:
                original = tokens.get_token(current_editing_word_number_range - 1)
            else:
                original = " ".join(tokens.get_tokens(current_editing_word_number_range[0] - 1, current_editing_word_number_range[1]))
            actions.user.correction_chicken_add_correction_rule(original, replacement)

    def correction_chicken_add_missing_text_to_the_end(word_number: int, text: str):
        """Make the ending of the word match the text preserving already present characters"""
        global tokens
        token = tokens.get_token(word_number - 1)
        biggest_prefix_size = compute_biggest_prefix_size_at_the_end_of_text(token, text)
        new_token = token + text[biggest_prefix_size:]
        tokens.set_token(word_number - 1, new_token)
        actions.user.correction_chicken_replace_text_with_tokens()

    def correction_chicken_get_last_word_with_homophones_number():
        """Get the number of the last word that is a homophone"""
        global tokens
        words = tokens.get_words()
        for index in range(len(words) - 1, -1, -1):
            word = words[index]
            if actions.user.correction_chicken_get_homophones(word):
                return tokens.get_word_index(index) + 1
        return -1

    def correction_chicken_homophones_advance_word(word_number: int=0):
        """Advance the word to the next homophone"""
        if word_number == 0:
            word_number = actions.user.correction_chicken_get_last_word_with_homophones_number()
            if word_number == -1:
                return

        global tokens
        word = tokens.get_token(word_number - 1)
        homophones = actions.user.correction_chicken_get_homophones(word)
        if homophones:
            index = homophones.index(word.lower())
            index = (index + 1) % len(homophones)
            actions.user.correction_chicken_replace_word_with_same_casing(word_number, homophones[index])
        
    def correction_chicken_get_homophones_other_than_word(word: str):
        """Get the homophones for the specified word other than the word itself"""
        homophones = actions.user.correction_chicken_get_homophones(word)
        result = [homophone for homophone in homophones if homophone != word.lower()]
        return result

    def correction_chicken_change_word_to_homophone_with_most_occurrences_of_character(word_number: int, character: str):
        """Change the word to the homophone with the most occurrences of the specified character"""
        global tokens
        word = tokens.get_token(word_number - 1)
        homophones = actions.user.correction_chicken_get_homophones_other_than_word(word)
        if homophones:
            occurrences = [homophone.count(character) for homophone in homophones]
            index = occurrences.index(max(occurrences))
            actions.user.correction_chicken_replace_word_with_same_casing(word_number, homophones[index])

    def correction_chicken_change_word_to_homophone_containing_characters(word_number: int, characters: List[str]):
        """Change the word to the homophone containing the specified characters"""
        global tokens
        word = tokens.get_token(word_number - 1)
        homophones = actions.user.correction_chicken_get_homophones_other_than_word(word)
        sub_string = "".join(characters)
        if homophones:
            for homophone in homophones:
                if sub_string in homophone:
                    actions.user.correction_chicken_replace_word_with_same_casing(word_number, homophone)
                    break
    
    def correction_chicken_change_last_homophone_with_alternative_containing_characters(characters: List[str]):
        """Find the last word with a homophone containing the specified characters and change it to that homophone"""
        global tokens
        words = tokens.get_words()
        sub_string = "".join(characters)
        for index in range(len(words) - 1, -1, -1):
            homophones = actions.user.correction_chicken_get_homophones_other_than_word(words[index])
            if homophones:
                for homophone in homophones:
                    if sub_string in homophone:
                        word_number = tokens.get_word_index(index) + 1
                        actions.user.correction_chicken_replace_word_with_same_casing(word_number, homophone)
                        return

    def correction_chicken_changed_last_homophone_with_character_to_alternative_with_most_instances_of_that_character(character: str):
        """Find the last word with a homophone containing the specified character and change it to the homophone with the most instances of that character"""
        global tokens
        words = tokens.get_words()
        for index in range(len(words) - 1, -1, -1):
            homophones = actions.user.correction_chicken_get_homophones_other_than_word(words[index])
            if homophones:
                occurrences = [homophone.count(character) for homophone in homophones]
                best_index = occurrences.index(max(occurrences))
                if occurrences[best_index] > 0:
                    word_number = tokens.get_word_index(index) + 1
                    actions.user.correction_chicken_replace_word_with_same_casing(word_number, homophones[best_index])
                    return

    def correction_chicken_perform_correction(correction_number: int):
        """Perform the specified correction"""
        global corrections
        correction = corrections[correction_number - 1]
        replacement = correction.replacement
        index = correction.starting_index
        post_index = index + len(correction.original)
        if not correction.casing_override:
            original_text_getting_replaced = last_phrase[index:post_index]
            casing = Casing.from_word(original_text_getting_replaced)
            replacement = casing.convert(replacement)
        new_text = last_phrase[:index] + replacement
        if post_index < len(last_phrase):
            new_text += last_phrase[index + len(correction.original):]
        actions.user.correction_chicken_replace_text(new_text)
    
    def correction_chicken_re_case_words(start_number: int, end_number: int, casing: str):
        """Change the casing of the specified words"""
        global tokens
        for i in range(start_number - 1, end_number):
            word = tokens.get_token(i)
            converted_word = apply_speakable_casing(casing, word)
            tokens.set_token(i, converted_word)
        actions.user.correction_chicken_replace_text_with_tokens()

    def correction_chicken_re_case_word(word_number: int, casing: str):
        """Change the casing of the specified word"""
        actions.user.correction_chicken_re_case_words(word_number, word_number, casing)
    
@imgui.open(y=0)
def gui(gui: imgui.GUI):
    global last_phrase, phrase_numbering, replacement, current_editing_word_number_range, tokens
    gui.text(phrase_numbering)
    gui.line()
    for index, correction_text in enumerate(correction_texts):
        gui.text(f"{index + 1}. {correction_text}")
    if replacement:
        gui.line()
        gui.text(replacement)
    if current_editing_word_number_range:
        gui.line()
        gui.text(current_editing_word_number_range)