tag: user.correction_chicken
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

remove <number_small>:
    user.correction_chicken_remove_word(number_small)

smush <number_small>:
    user.correction_chicken_remove_separator(number_small)

Eddie <number_small>:
    user.correction_chicken_add_missing_text_to_the_end(number_small, "ed")

phony [<number_small>]:
    user.correction_chicken_homophones_advance_word(number_small or 0)

phony <user.letter>:
    user.correction_chicken_changed_last_homophone_with_character_to_alternative_with_most_instances_of_that_character(user.letter)

phony <user.letter> <number_small>:
    user.correction_chicken_change_word_to_homophone_with_most_occurrences_of_character(number_small, user.letter)

phony <user.letter>+ :
    user.correction_chicken_change_last_homophone_with_alternative_containing_characters(user.letter_list)

phony <user.letter>+ <number_small>:
    user.correction_chicken_change_word_to_homophone_containing_characters(number_small, user.letter_list)

court <number_small>:
    user.correction_chicken_perform_correction(number_small)

spelling <number_small> <user.letter>+:
    user.correction_chicken_spell_out_alternative_for_word(user.letter_list, number_small)

spelling <user.letter>+:
    user.correction_chicken_spell_out_alternative_for_word(user.letter_list)

spelling <number_small>:
    user.correction_chicken_choose_word_for_replacement(number_small)

spelling <number_small> through <number_small>:
    user.fire_chicken_choosing_range_for_replacement(number_small_1, number_small_2)

phrasing <user.prose>:
    user.correction_chicken_set_replacement(prose)

wording <user.word>:
    user.correction_chicken_set_replacement(word)

wording <number_small> <user.word>:
    user.correction_chicken_choose_word_for_replacement(number_small)
    user.correction_chicken_set_replacement(word)

correct that:
    user.correction_chicken_set_last_phrase_to_selected_text()

correct line:
    edit.select_line()
    user.correction_chicken_set_last_phrase_to_selected_text()

case {user.correction_chicken_casing} <number_small>:
    user.correction_chicken_re_case_word(number_small, correction_chicken_casing)

case {user.correction_chicken_casing} <number_small> through <number_small>:
    user.correction_chicken_re_case_words(number_small_1, number_small_2, correction_chicken_casing)

correction chicken move [display]: user.correction_chicken_set_display_position_to_current_mouse_position()