# provides code for updating the correction graphical interface

from talon import actions, Module, app, cron, settings, Context
from .canvas import Display, Items

MINIMUM_CORRECTION_LINE_LENGTH: int = 20

display = Display()
graphics_timeout_job = None
is_active: bool = False
context = Context()

# on startup, load the position for the display from disk
def on_ready():
	top, right = actions.user.correction_chicken_load_display_position()
	display.set_position(top, right)
app.register("ready", on_ready)

def have_graphics_handle_activity():
	global graphics_timeout_job
	if graphics_timeout_job:
		cron.cancel(graphics_timeout_job)
	if is_active and not display.is_showing():
		display.show()
	time_out_amount = settings.get("user.correction_chicken_graphics_time_out")
	if time_out_amount > 0:
		graphics_timeout_job = cron.after(f"{time_out_amount}s", display.hide)

def cancel_graphics_timeout_job():
	global graphics_timeout_job
	if graphics_timeout_job:
		cron.cancel(graphics_timeout_job)
		graphics_timeout_job = None

def compute_correction_text_with_numbering(index, text):
	return f"{index + 1}. {text}"

def show_correction_options(phrase_numbering, correction_texts, items: Items):
	correction_line = ""
	for index, correction_text in enumerate(correction_texts):
		option_text = compute_correction_text_with_numbering(index, correction_text)
		if correction_line and len(correction_line) + len(option_text) + 1 < max(len(phrase_numbering), MINIMUM_CORRECTION_LINE_LENGTH):
			correction_line += " " + option_text
		else:
			if correction_line:
				items.text(correction_line)
				correction_line = ""
			correction_line = option_text
	if correction_line:
		items.text(correction_line)

def update_display(
	phrase_numbering,
	replacement: str,
	correction_texts: list[str],
	current_editing_word_number_range):
	items = Items()
	items.text(phrase_numbering)
	items.line()

	show_correction_options(phrase_numbering, correction_texts, items)
	if replacement:
		items.line()
		items.text(replacement)
	if current_editing_word_number_range:
		items.line()
		items.text(str(current_editing_word_number_range))
	display.update(items)
	if is_active:
		display.refresh()

mod = Module()
@mod.action_class
class Actions:
	def correction_chicken_toggle():
		"""Toggles correction chicken"""
		global is_active
		if is_active:
			context.tags = []
			display.hide()
			cancel_graphics_timeout_job()
		else:
			context.tags = ["user.correction_chicken"]
			display.show()
			have_graphics_handle_activity()
		is_active = not is_active

	def correction_chicken_set_display_position_to_current_mouse_position():
		"""Set the display position to the current mouse position"""
		global display
		x = int(actions.mouse_x())
		y = int(actions.mouse_y())
		display.set_position(x, y)
		actions.user.correction_chicken_save_display_position(x, y)
		if is_active:
			display.refresh()
		have_graphics_handle_activity()