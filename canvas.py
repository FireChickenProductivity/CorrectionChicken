#Goals
#custom scaling size
#ability to move location through voice commands
#ability to save location
#Size based on input text
#Ability to set background color
#Ability to set text color
#ability to set text and add vertical bars

from talon import canvas, ui, skia
from talon.skia import Paint, Rect

class VerticalBar: pass

class Items:
	def __init__(self):
		self.items = []
	
	def text(self, text):	
		self.items.append(text)

	def line(self):
		self.items.append(VerticalBar())

	def get_items(self):	
		return self.items

class Display:
	def __init__(self):
		self.scaling_factor = 1.0
		self.canvas = None
		self.left = 0
		self.top = 0
		self.items: Items = Items()
		self.background_color = "#FFFFFF"  # White
		self.foreground_color = "#000000"  # Black

	def update(self, items: Items):
		self.items = items
	   
	def show(self):
		self.canvas = canvas.Canvas.from_screen(ui.screens()[0])
		self.showing = True
		self.canvas.register("draw", self.draw)
		self.canvas.freeze()
		return 

	def draw(self, canvas):
		canvas.paint.text_align = canvas.paint.TextAlign.LEFT
		text_size = 10 * self.scaling_factor
		canvas.paint.textsize = text_size
		canvas.paint.style = Paint.Style.FILL
		canvas.paint.color = self.background_color
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
		rounded_rectangle = skia.RoundRect.from_rect(backround_rectangle, x=10, y=10)

		canvas.draw_rrect(rounded_rectangle)
		canvas.paint.color = self.foreground_color
		y = self.top + 0.5*text_size
		for i, item in enumerate(self.items.get_items()):
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

	def set_scaling_factor(self, scaling_factor):
		self.scaling_factor = scaling_factor
		self.refresh()

	def set_foreground_color(self, color: str):
		self.foreground_color = color
		self.refresh()

	def set_background_color(self, color: str):
		self.background_color = color
		self.refresh()