from talon import fs, Module
import os
from pathlib import Path
import csv
from typing import List

class Correction:
    __slots__ = ('starting_index', 'original', 'replacement', 'casing_override')
    def __init__(self, starting_index, original, replacement, casing_override):
        self.starting_index = starting_index
        self.original = original
        self.replacement = replacement
        self.casing_override = casing_override
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"Correction(at {self.starting_index}:{self.original}->{self.replacement} Casing Override: {self.casing_override})"

STANDARD_CASING = ''
EXACT_CASING = 'exact'

class SimpleCorrectionRule:
    __slots__ = ('original', 'replacement', 'case_override')
    def __init__(self, original: str, replacement: str, case_override: str):
        self.original = original
        self.replacement = replacement
        self.case_override = case_override
    
    @staticmethod
    def make_from_row(row):
        original: str = row[0].lower()
        replacement: str = row[1]
        case_override: str = STANDARD_CASING
        if len(row) > 2:
            case_override = row[2]
        rule = SimpleCorrectionRule(original, replacement, case_override)
        return rule
    
    def get_original(self):
        return self.original
    
    def get_replacement(self):
        return self.replacement
    
    def __str__(self) -> str:
        return f'(SimpleCorrectionRule: "{self.original}" to "{self.replacement}" with casing "{self.case_override}")'
    
    def __repr__(self) -> str:
        return self.__str__()

CORRECTION_DIRECTORY = Path(__file__).parents[0] / "correction_data"

def get_correction_file_names():
    correction_directory = CORRECTION_DIRECTORY
    relative_names = os.listdir(correction_directory)
    absolute_names = []
    for name in relative_names:
        absolute_names.append(os.path.join(correction_directory, name))
    return absolute_names

class SimpleCorrectionRules:
    __slots__ = ('rules')
    def __init__(self):
        self.rules = {}
        file_names = get_correction_file_names()
        for file in file_names:
            self.add_rules_from_file(file)
    
    def add_rules_from_file(self, name):
        with open(str(name), "r") as file:
            reader = csv.reader(file)
            for row in reader:
                self.add_rule_from_row(row)
            
    def add_rule_from_row(self, row):
        rule: SimpleCorrectionRule = SimpleCorrectionRule.make_from_row(row)
        if rule.get_original() not in self.rules:
            self.rules[rule.get_original()] = []
        self.rules[rule.get_original()].append(rule)
    
    def compute_corrections_for_text(self, text: str, starting_index) -> list[Correction]:
        corrections = []
        lower_case_text: str = text.lower()
        if lower_case_text in self.rules:
            for rule in self.rules[lower_case_text]:
                corrections.append(Correction(starting_index, rule.get_original(), rule.get_replacement(), rule.case_override))
        return corrections

if not os.path.exists(CORRECTION_DIRECTORY):
    os.makedirs(CORRECTION_DIRECTORY, exist_ok=True)
rules = SimpleCorrectionRules()

def on_correction_file_update(path, flags):
    global rules
    rules = SimpleCorrectionRules()
fs.watch(CORRECTION_DIRECTORY, on_correction_file_update)

def compute_every_sub_string(text: str):
    for i in range(len(text)):
        for j in range(i + 1, len(text) + 1):
            yield (i, text[i:j])
 
def compute_possible_corrections_for_text(text: str) -> list[Correction]:
    corrections = []
    lower_case_text: str = text.lower()
    sub_strings = compute_every_sub_string(lower_case_text)
    for starting_index, sub_string in sub_strings:
        corrections.extend(rules.compute_corrections_for_text(sub_string, starting_index))
    return corrections

module = Module()
@module.action_class
class Actions:
    def correction_chicken_compute_corrections_for_phrase(phrase: str) -> List[Correction]:
        """Compute corrections for the specified phrase"""
        return compute_possible_corrections_for_text(phrase)

    def correction_chicken_add_correction_rule(original: str, replacement: str, case_override: str=""):
        """Add a correction rule"""
        with open((os.path.join(CORRECTION_DIRECTORY, 'added.csv')), "a") as file:
            writer = csv.writer(file)
            writer.writerow([original, replacement, case_override])