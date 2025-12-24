from .tokenization import Tokens

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

def compute_last_alphabetic_index_and_casing(tokens: Tokens, end_index):
    for i in range(end_index, -1, -1):
        if tokens.get_token(i).isalpha():
            return i, Casing.from_word(tokens.get_token(i))
    return None, None

def compute_first_alphabetic_index_and_casing(tokens: Tokens, start_index):
    for i in range(start_index, tokens.get_size()):
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

def replace_tokens_with_matching_casing(tokens: Tokens, index_range, replacement: str):
    start_number, end_number = index_range
    relevant_tokens = tokens.get_tokens(start_number - 1, end_number)
    tokens_for_replacement = Tokens(replacement)
    replacement_tokens = tokens_for_replacement.get_tokens(0, tokens_for_replacement.get_size())
    last_casing = compute_before_casing(tokens, start_number)
    after_casing = compute_after_casing(tokens, end_number)
    new_tokens = create_tokens_with_matching_casing(replacement_tokens, relevant_tokens, last_casing, after_casing)
    tokens.set_tokens(start_number - 1, end_number, new_tokens)