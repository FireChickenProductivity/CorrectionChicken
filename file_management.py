import os
from pathlib import Path

from talon import Module, app

DISPLAY_CONFIGURATION_DIRECTORY = Path(__file__).parents[0] / "display_configuration"
os.makedirs(DISPLAY_CONFIGURATION_DIRECTORY, exist_ok=True)
DISPLAY_POSITION_FILE = DISPLAY_CONFIGURATION_DIRECTORY / "display_position.txt"

module = Module()
@module.action_class
class Actions:
	def correction_chicken_save_display_position(left: int, top: int):
		"""Saves the display position to a file."""
		with open(DISPLAY_POSITION_FILE, "w") as file:
			file.write(f"{left},{top}")

	def correction_chicken_load_display_position() -> tuple[int, int]:
		"""Loads the display position from a file."""
		if DISPLAY_POSITION_FILE.exists():
			with open(DISPLAY_POSITION_FILE, "r") as file:
				content = file.read().strip()
				coordinates = content.split(",")
				if len(coordinates) != 2 or \
					not all(coord.isdigit() for coord in coordinates):
					app.notify("The correction chicken file containing the position for the display has been corrupted. Resetting the display position with \"correction chicken move\" should fix this issue.")
					return 0, 0
				left, top = map(int, coordinates)
				return left, top
		return 0, 0