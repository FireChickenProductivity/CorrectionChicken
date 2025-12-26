# this file contains support for computing and manipulating the cases of words

from .tokenization import Tokens

class Casing:
    """Represents the case of a token or multiple tokens"""
    LOWERCASE = 1
    CAPITALIZED = 2
    UPPERCASE = 3
    OTHER = 4
    def __init__(self, casing: int):
        self.casing = casing

    @staticmethod
    def from_word(word: str):
        """Compute the case of a word"""
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
        """Compute the specified word converted to the Casing"""
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

def create_tokens_with_matching_casing(
    replacement_tokens: list[str],
    relevant_tokens: list[str],
    last_casing: Casing,
    after_casing: Casing):
    """
        Compute the casing of relevant_tokens
        and then return it applied to replacement_tokens
        after_casing: the casing to use for tokens in replacement_tokens
        with index greater than any index of relevant_tokens
        last_casing: the casing before the current token
        this could be based on a token in the original set of tokens before relevant_tokens
    """
    # the index of the next alphabetic token in relevant_tokens
    next_index = 0
    new_tokens = []
    for index, replacement_token in enumerate(replacement_tokens):
        # if the index of the replacement token also corresponds to an index in relevant_tokens corresponding to an alphabetic token
        # use the casing of that word
        if index < len(relevant_tokens) and relevant_tokens[index].isalpha():
            casing = Casing.from_word(relevant_tokens[index])
        else:
            if next_index <= index:
                # keep incrementing next_index until it is greater than index and
                # (goes past the indexes of relevant_tokens
                # or refers to an alphabetic token in relevant_tokens)
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
    """
        Find the ideal casing for a replacement token considering the previous and following casings
        
    """
    # with no other information just use the token casing
    if not last_casing and not next_casing:
        casing = Casing.from_word(replacement_token)
    # if one casing is missing use the other. if they have the same value, use it
    elif not next_casing:
        casing = last_casing
    elif (not last_casing) or (last_casing == next_casing):
        casing = next_casing
    # otherwise use the lowest casing between the last and next
    elif last_casing < next_casing:
        casing = last_casing
    else:
        casing = next_casing
    return casing

def compute_last_alphabetic_index_and_casing(tokens: Tokens, end_index: int):
    """Compute the index and casing of the last alphabetic token starting from end_index"""
    for i in range(end_index, -1, -1):
        if tokens.get_token(i).isalpha():
            return i, Casing.from_word(tokens.get_token(i))
    return None, None

def compute_first_alphabetic_index_and_casing(tokens: Tokens, start_index: int):
    """Compute the index and casing of the first alphabetic token starting from start_index"""
    for i in range(start_index, tokens.get_size()):
        if tokens.get_token(i).isalpha():
            return i, Casing.from_word(tokens.get_token(i))
    return None, None

def compute_before_casing(tokens: Tokens, start_number: int):
    """Find the casing of the token before the start number (numbering = index+1)"""
    if start_number > 1:
        first_index, first_casing = compute_first_alphabetic_index_and_casing(tokens, start_number - 2)
        if first_index is not None and first_index + 1 < start_number:
            last_casing = first_casing
        else:
            last_casing = None
    else:
        last_casing = None
    return last_casing

def compute_after_casing(tokens: Tokens, end_number: int):
    """Find the casing of the token after the end_number (numbering = index+1)"""
    if end_number < tokens.get_size():
        last_index, last_casing = compute_last_alphabetic_index_and_casing(tokens, end_number)
        if last_index is not None and last_index + 1 > end_number:
            after_casing = last_casing
        else:
            after_casing = None
    else:
        after_casing = None
    return after_casing

SPEAKABLE_CASINGS = {
    "LOWER": Casing.LOWERCASE,
    "CAPITALIZED": Casing.CAPITALIZED,
    "UPPER": Casing.UPPERCASE,
}

def apply_speakable_casing(spoken_form, target):
    case = SPEAKABLE_CASINGS[spoken_form]
    casing = Casing(case)
    return casing.convert(target)

def replace_tokens_with_matching_casing(
    tokens: Tokens,
    index_range: tuple[int, int],
    replacement: str):
    """Replace the tokens in the index range with the replacement string
        with replacement tokens converted to casings matching the tokens at
        corresponding indexes
    """
    start_number, end_number = index_range
    relevant_tokens = tokens.get_tokens(start_number - 1, end_number)
    tokens_for_replacement = Tokens(replacement)
    replacement_tokens = tokens_for_replacement.get_tokens(0, tokens_for_replacement.get_size())
    last_casing = compute_before_casing(tokens, start_number)
    after_casing = compute_after_casing(tokens, end_number)
    new_tokens = create_tokens_with_matching_casing(replacement_tokens, relevant_tokens, last_casing, after_casing)
    tokens.set_tokens(start_number - 1, end_number, new_tokens)