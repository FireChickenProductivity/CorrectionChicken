# this file provides support for separating text into tokens

from typing import Optional

from talon import actions

def is_token_over(token: str, next_character: str, next_next_character: Optional[str]):
	"""Decides if the current token is over
	The input text is parsed by iterating over the indexes and using this 
	function to decide when one token ends and the next one starts
	token: text currently considered part of the token
	next_character: the next character from the input text
	next_next_character: the character after the next character from the input text
	"""
	# if the token is empty, add the next character to it
	if not token:
		return False
	last_character = token[-1]
	# If the next or last character is a single quote, make sure that contractions and possessive forms are not token endings
	if next_character == "'" and (next_next_character and (next_next_character.isalpha() or next_next_character.isspace()) and last_character.isalpha()):
		return False
	elif last_character == "'" and (len(token) > 1 and token[-2].isalpha() and (next_character.isalpha())):
		return False
	# new token if next character is the start of a capitalized word,
	# there is a space,
	# or this denotes the last in a sequence of consecutive alphabetic or consecutive non alphabetic characters
	return (last_character.isalpha() != next_character.isalpha()) or \
			next_character.isspace() or \
			(last_character.islower() and next_character.isupper())

class Tokens:
	"""Represents text divided into tokens"""
	__slots__ = ('tokens', 'spacing', 'word_indexes')
	def _add_token(self, token: str, spaces: str):
		"""When the end of a token is encountered, store token related information"""
		self.tokens.append(token)
		if len(self.tokens) > 1:
			self.spacing.append(spaces)
		if token[-1].isalpha():
			self.word_indexes.append(len(self.tokens) - 1)

	def __init__(self, text):
		text = text.lstrip()
		# self.tokens: the tokens from the text
		self.tokens = []
		# self.spacing: contains the spacing in between the tokens
		self.spacing = []
		# self.word_indexes: contains the indexes of the tokens that are words
		self.word_indexes = []
		spaces = ""
		token = ""
		# for every position in the text: 
		# 	update token related data if the end of the current token has been encountered
		for index, character in enumerate(text):
			next_next_character = text[index + 1] if index + 1 < len(text) else None
			if is_token_over(token, character, next_next_character):
				self._add_token(token, spaces)
				spaces = ""
				token = ""
			if character.isspace():
				spaces += character
			else:
				token += character
		# makes sure the last token is included
		if token:
			self._add_token(token, spaces)
		self.spacing.append(spaces)

	def get_token(self, index: int) -> str:
		return self.tokens[index]

	def get_size(self) -> int:
		return len(self.tokens)
	
	def get_text(self) -> str:
		"""Return the tokens joined together separated by a space. 
			White space from the original text is ignored. 
		"""
		return " ".join(self.tokens)

	def set_token(self, index: int, new_token: str):
		"""Set the token at index to new_token"""
		self.tokens[index] = new_token

	def get_tokens(self, start_index: int, end_index: int) -> list[str]:
		return self.tokens[start_index:end_index]

	def set_tokens(self, start_index: int, end_index: int, tokens: list[str]):
		self.tokens[start_index:end_index] = tokens

	def get_words(self) -> list[str]:
		"""Return a list of tokens considered words"""
		return [self.get_token(index) for index in self.word_indexes]

	def set_word(self, index: int, word: str):
		"""Update the word at the specified index
			Note that the indexing is in terms of the words rather than tokens.
			i.e. Using zero as the index here refers to the first word and not the first token
		"""
		self.tokens[self.word_indexes[index]] = word

	def get_word(self, index: int) -> str:
		"""Get the word indexing in terms of the words as if they were in a separate list"""
		return self.tokens[self.word_indexes[index]]

	def get_word_index(self, index: int) -> int:
		"""Get the token index corresponding to the word"""
		return self.word_indexes[index]
	
	def remove_token(self, index: int):
		self.tokens.pop(index)

	def remove_separator(self, index: int):
		"""Remove the specified separating characters in between words."""
		if index in self.word_indexes:
			next_word_index: Optional[int] = None
			# find the index of the word after the current word
			for i in self.word_indexes:
				if i > index:
					next_word_index = i
					break
			
			if next_word_index is not None:
				spacing = self.spacing[index]
				# If The words are next to each other with no spacing between them, there is nothing to remove
				if spacing or next_word_index > index + 1:
					self.spacing.pop(index)
					next_word = self.tokens.pop(next_word_index)
					self.tokens[index] += next_word
					if next_word_index > index + 1:
						self.tokens.pop(index + 1) 
						#Remove the spacing for the removed separator
						self.spacing.pop(index)
	
	def get_overlapping_tokens_length(
		self,
		original_text_start_index: int,
		original_text_final_index) -> int:
		"""Finds the length of the tokens corresponding to the indexes in the original text"""
		if original_text_start_index > original_text_final_index:
			raise ValueError(f"Received start index {original_text_start_index} exceeding final index {original_text_final_index}")
		current_length: int = 0
		start_index = None
		ending_index = None
		# when the total length found so far exceeds one of the original indexes
		# we have found the containing token
		for i, token in enumerate(self.tokens):
			current_length += len(token) + len(self.spacing[i])
			if start_index is None and current_length > original_text_start_index:
				start_index = i
			if ending_index is None and current_length > original_text_final_index:
				ending_index = i + 1
				break
		if start_index is None or ending_index is None:
			# fail in a way that lets the rest of the system work
			actions.app.notify(f"An error occurred computing the amount of overlap between a Correction Chicken correction rule and text. Please notify the developer! tokens: {self.tokens}, original start {original_text_start_index}, original final {original_text_final_index}")
			return 0
		# now that we know the indexes, sum up the corresponding lengths
		count: int = 0
		for i in range(start_index, ending_index):
			count += len(self.tokens[i])
			count += len(self.spacing[i])
		return count

	def __repr__(self):
		return self.__str__()
	
	def __str__(self):
		result = ""
		for i in range(len(self.tokens)):
			result += self.tokens[i] + self.spacing[i]
		return result

	def __eq__(self, value: object) -> bool:
		return isinstance(value, Tokens) and self.tokens == value.tokens