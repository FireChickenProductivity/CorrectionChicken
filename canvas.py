# Provides support for graphics
# provides a high level interface to a low level canvas
# the rest of the project relies on this for displaying information

from talon import canvas, ui, skia, Module, settings
from talon.skia import Paint, Rect

module = Module()

module.setting(
	'correction_chicken_display_scale',
	type = float,
	default = 1.0,
	desc = 'The scale for the correction chicken display. Increase this to make it bigger and decrease it to make it smaller.',
)
module.setting(
	'correction_chicken_background_color',
	type = str,
	default = "#FFFFFF",  # Default to white
	desc = 'This is the correction chicken display background color.'
)
module.setting(
	'correction_chicken_foreground_color',
	type = str,
	default = "#000000",  # Default to black
	desc = 'This is the correction chicken display foreground color.'
)

class VerticalBar: pass

class Items:
	__slots__ = ('items')
	def __init__(self):
		self.items = []
	
	def text(self, text):	
		self.items.append(text)

	def line(self):
		self.items.append(VerticalBar())

	def get_items(self):	
		return self.items

class Display:
	__slots__ = ('canvas', 'left', 'top', 'items', 'showing')
	def __init__(self):
		self.canvas = None
		self.left = 0
		self.top = 0
		self.items: Items = Items()
		self.showing = False

	def update(self, items: Items):
		self.items = items
	   
	def show(self):
		self.canvas = canvas.Canvas.from_screen(ui.screen_containing(self.left, self.top))
		self.showing = True
		self.canvas.register("draw", self.draw)
		self.canvas.freeze()
		return 

	def draw(self, canvas):
		canvas.paint.text_align = canvas.paint.TextAlign.LEFT
		text_size = 10 * settings.get('user.correction_chicken_display_scale')
		canvas.paint.textsize = text_size
		canvas.paint.style = Paint.Style.FILL
		height = 0
		width = 0
		for item in self.items.get_items():
			if isinstance(item, str):
				width = max(width, canvas.paint.measure_text(item)[1].width)
				height += 1
			elif isinstance(item, VerticalBar):
				height += 0.5
		right = self.left + width + text_size
		bottom = self.top + height * text_size * 1.5 + text_size
		backround_rectangle = Rect(self.left, self.top, right - self.left, bottom - self.top)
		outline_rectangle = Rect(self.left - 1, self.top - 1, right - self.left + 2, bottom - self.top + 2)
		rounded_rectangle = skia.RoundRect.from_rect(backround_rectangle, x=10, y=10)
		rounded_outline_rectangle = skia.RoundRect.from_rect(outline_rectangle, x=10, y=10)

		canvas.paint.color = settings.get('user.correction_chicken_foreground_color')
		canvas.draw_rrect(rounded_outline_rectangle)
		canvas.paint.color = settings.get('user.correction_chicken_background_color')
		canvas.draw_rrect(rounded_rectangle)
		canvas.paint.color = settings.get('user.correction_chicken_foreground_color')
		y = self.top + 0.5*text_size
		for item in self.items.get_items():
			if isinstance(item, str):
				y += round(1.5*text_size)
				canvas.draw_text(item, self.left + 0.5*text_size, y)
			elif isinstance(item, VerticalBar):
				y += round(text_size / 2)
				canvas.draw_line(self.left, y, right, y)


	def hide(self):
		self.showing = False
		if self.canvas:
			self.canvas.close()

	def is_showing(self):
		return self.showing
	
	def refresh(self):
		if self.is_showing():
			self.hide()
			self.show()

	def set_position(self, left: int, top: int):
		self.left = left
		self.top = top
		self.refresh()
