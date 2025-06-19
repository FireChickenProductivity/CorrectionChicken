from talon import actions, speech_system
from collections import Counter

from pathlib import Path
vocabulary = Counter()
VOCABULARY_FILE = Path(__file__).parents[0] / "vocabulary.txt"
if VOCABULARY_FILE.exists():
    with open(VOCABULARY_FILE, "r") as file:
        for line in file:
            word, count = line.strip().split(":")
            vocabulary[word.lower()] += int(count)

last_words = []
def on_phrase(j):
    global last_words
    words = j.get("phrase")
    if words and words != last_words:
        last_words = words
        for word in words:
            vocabulary.update([word.lower()])
    actions.user.correction_chicken_update_last_phrase(actions.user.correction_chicken_get_last_phrase())


speech_system.register("post:phrase", on_phrase)

from talon import Module
module = Module()
@module.action_class
class Actions:
    def correction_chicken_save_vocabulary():
        """Updates the vocabulary"""
        with open(VOCABULARY_FILE, "w") as file:
            for word, count in vocabulary.items():
                file.write(f"{word}:{count}\n")