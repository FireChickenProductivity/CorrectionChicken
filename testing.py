if False:
    from .correction import *
    def perform_single_output_table_testing(table, function, in_place_index=None):
        failures = 0
        for index, entry in enumerate(table):
            expected_output = entry[-1]
            input_values = entry[:-1]
            input_text = str(input_values)
            if in_place_index is not None:
                function(*input_values)
                actual_output = input_values[in_place_index]
            else:
                actual_output = function(*input_values)
            if actual_output != expected_output:
                print(f"Test {index + 1} failed: {input_text} -> expected {expected_output} != actual {actual_output}")
                failures += 1
        if failures == 0:
            print("All tests passed.")
        
    replacing_tokens_with_matching_casing_table = [
        (Tokens('this is a test'), (1, 2), "TESTING", Tokens("testing a test")),
        (Tokens('This Is A Test'), (1, 2), "TESTING Exactly", Tokens("Testing Exactly A Test")),
        (Tokens('this is a test'), (1, 2), "TESTING Excessively a", Tokens("testing excessively a a test")),
        (Tokens('this is a test'), (1, 4), "TESTING A TESTED TEST", Tokens("testing a tested test")),
        (Tokens("This, IS, a, Test"), (1, 7), "new words for a very special test", Tokens("New Words FOR a very special Test")),
        (Tokens("IS, . This, a, "), (1, 7), "new words for a very special test", Tokens("NEW Words For A very special test")),
        (Tokens("this, is"), (1, 3), "Words Are Irrelevant", Tokens("words are irrelevant")),
        (Tokens("This, Is"), (1, 3), "Words Are Irrelevant", Tokens("Words Are Irrelevant")),
        (Tokens("This, IS"), (2, 3), "Are Irrelevant", Tokens("This Are IRRELEVANT")),
        (Tokens("IS, This"), (1, 2), "Are Irrelevant", Tokens("ARE Irrelevant This")),
    ]
    perform_single_output_table_testing(replacing_tokens_with_matching_casing_table, replace_tokens_with_matching_casing, in_place_index=0)
