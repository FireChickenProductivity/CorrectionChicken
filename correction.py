from talon import Module, actions, Context, settings
from typing import List, Union, Tuple, Optional
from .tokenization import Tokens
from .casing import apply_speakable_casing, Casing, replace_tokens_with_matching_casing
from .correction_display import update_display, have_graphics_handle_activity

last_phrase: str = ""
phrase_numbering: str = ""
tokens: Optional[Tokens] = None
corrections: list = []
correction_texts: list[str] = []
replacement: str = ""
current_editing_word_number_range = None

def compute_biggest_prefix_size_at_the_end_of_text(text: str, prefix: str) -> int:
    """Compute biggest common prefix length between the prefix and the string"""
    for i in range(len(prefix), 0, -1):
        if text.endswith(prefix[:i]):
            return i
    return 0

def compute_number_of_leading_spaces(text: str) -> int:
    """Compute number of spaces at the start of the text"""
    number_of_leading_spaces = 0
    while number_of_leading_spaces < len(text) and text[number_of_leading_spaces].isspace():
        number_of_leading_spaces += 1
    return number_of_leading_spaces

def compute_common_prefix_size(a: str, b: str) -> int:
    """Compute the number of consecutive characters starting from the first index
        that a and b have in common
    """
    size = 0
    minimum_length = min(len(a), len(b))
    while size < minimum_length and a[size] == b[size]:
        size += 1
    return size

def replace_text_through_deletion_and_insertion(original: str, replacement: str):
    """Use key presses to replace the original with the replacement"""
    common_prefix_size = compute_common_prefix_size(original, replacement)
    for _ in range(len(original) - common_prefix_size):
        actions.edit.delete()
    actions.sleep(0.1)
    trimmed_replacement = replacement[common_prefix_size:]
    actions.insert(trimmed_replacement)

def replace_text_through_selection_and_pasting(original: str, replacement: str, line_limit: int):
    actions.edit.extend_line_start()
    text: str = actions.edit.selected_text()
    remaining_lines = line_limit - 1
    while original not in text and remaining_lines > 0:
        actions.edit.extend_line_up()
        actions.edit.extend_line_start()
        text = actions.edit.selected_text()
        remaining_lines -= 1
    original_location = text.rfind(original)
    if original_location > -1:
        new_text = text[:original_location] + replacement + text[original_location + len(original):]
        actions.user.paste(new_text)
    else:
        actions.edit.right()

module = Module()
module.list("correction_chicken_casing", desc="Casing options")
module.tag("correction_chicken_replacement", desc="Enables replacement commands for correction chicken")
module.tag("correction_chicken", desc="Activates correction chicken commands")
replacement_context = Context()

module.setting(
    'correction_chicken_graphics_time_out',
    type = float,
    default = 60,
    desc = "How long to keep the correction chicken graphics open without a correction chicken command or dictation getting used in seconds"
)
module.setting(
    'correction_chicken_correction_percentage_match_threshold',
    type = float,
    default = 0.5,
    desc = "Requires a correction option to match more than this percentage of a word. 0.0 means show all options."
)
module.setting(
    'correction_chicken_correction_hunt_distance',
    type = int,
    default = 0,
    desc = "How many lines to search for the text to correct in the document using selection. 0 means not searching at all."
)

@module.action_class
class Actions:
    def correction_chicken_update_last_phrase(phrase: str):
        """Update the last phrase dictated"""
        global last_phrase, phrase_numbering, corrections, correction_texts, tokens
        phrase = phrase.lstrip()
        if phrase != last_phrase:
            have_graphics_handle_activity()
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
            
            corrections = actions.user.correction_chicken_compute_corrections_for_phrase(phrase, tokens)
            
            correction_texts = [correction.original + " -> " + correction.replacement for correction in corrections]
            update_correction_display()

    def correction_chicken_set_last_phrase_to_selected_text():
        """Set the last phrase to the selected text"""
        selected_text = actions.user.correction_chicken_get_selected_text()
        actions.edit.right()
        actions.user.correction_chicken_update_last_phrase(selected_text)

    def correction_chicken_replace_text(replacement: str):
        """Replace the phrase with the specified text"""
        global last_phrase
        line_limit = settings.get("user.correction_chicken_correction_hunt_distance")
        if line_limit > 0:
            replace_text_through_selection_and_pasting(last_phrase, replacement, line_limit)
        else:
            replace_text_through_deletion_and_insertion(last_phrase, replacement)
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

    def correction_chicken_remove_word(word_number: int):
        """Remove the specified word"""
        global tokens
        tokens.remove_token(word_number - 1)
        actions.user.correction_chicken_replace_text_with_tokens()

    def correction_chicken_remove_separator(word_number: int):
        """Removes the separator after the specified word"""
        global tokens
        tokens.remove_separator(word_number - 1)
        actions.user.correction_chicken_replace_text_with_tokens()

    def correction_chicken_activate_replacement_context():
        """Activates the replacement context"""
        replacement_context.tags = ["user.correction_chicken_replacement"]

    def correction_chicken_deactivate_replacement_context():
        """Deactivates the replacement context"""
        replacement_context.tags = []

    def correction_chicken_set_current_number_range(range: Union[int, Tuple[int, int]]):
        """Set the current number range"""
        have_graphics_handle_activity()
        global current_editing_word_number_range
        current_editing_word_number_range = range
        actions.user.correction_chicken_activate_replacement_context()
        update_correction_display()

    def correction_chicken_spell_out_alternative_for_word(characters: List[str], word_number: int=None):
        """Spell out the alternative for the specified word"""
        global current_editing_word_number_range, replacement
        if word_number is not None:
            actions.user.correction_chicken_set_current_number_range(word_number)
        replacement = "".join(characters)
        actions.user.correction_chicken_set_replacement(replacement)
    
    def correction_chicken_set_replacement(new_replacement: str):
        """Set the replacement"""
        have_graphics_handle_activity()
        global replacement
        replacement = new_replacement
        update_correction_display()

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
    
def update_correction_display():
    update_display(phrase_numbering,
                   replacement,
                   correction_texts,
                   current_editing_word_number_range
                   )