from talon import actions, speech_system

def on_phrase(j):
    actions.user.correction_chicken_update_last_phrase(actions.user.correction_chicken_get_last_phrase())


speech_system.register("post:phrase", on_phrase)
