from talon import Module, actions

module = Module()
@module.action_class
class Actions:
    def correction_chicken_get_last_phrase() -> str:
        """Get the last phrase dictated"""
        return actions.user.get_last_phrase()

    def correction_chicken_get_selected_text() -> str:
        """Get the selected text"""
        return actions.edit.selected_text()

    def correction_chicken_set_last_phrase(phrase: str):
        """Sets the last phrase"""
        actions.user.add_phrase_to_history(phrase)

    def correction_chicken_get_homophones(word: str):
        """Get the homophones for the specified word"""
        phones = actions.user.homophones_get(word)
        if phones:
            phones = [phone.lower() for phone in phones]
            return phones[:]
        return []
