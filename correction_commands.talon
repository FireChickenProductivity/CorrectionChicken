mode: command
mode: dictation
-
trim <number_small>:
    user.correction_chicken_remove_characters_from_word(number_small, 1)

chop <number_small>:
    user.correction_chicken_remove_characters_from_word(number_small, 2)

plural <number_small>:
    user.correction_chicken_add_characters_to_word_ending(number_small, "s")

dual <number_small>:
    user.correction_chicken_add_characters_to_word_ending(number_small, "es")

correction chicken:
    user.correction_chicken_toggle()

remove <number_small>:
    user.correction_chicken_remove_word(number_small)

phony [<number_small>]:
    user.correction_chicken_homophones_advance_word(number_small or 0)

phony <user.letter> <number_small>:
    user.correction_chicken_change_word_to_homophone_with_most_occurrences_of_character(number_small, user.letter)

phony <user.letter>+ <number_small>:
    user.correction_chicken_change_word_to_homophone_containing_characters(number_small, user.letter_list)

court <number_small>:
    user.correction_chicken_perform_correction(number_small)