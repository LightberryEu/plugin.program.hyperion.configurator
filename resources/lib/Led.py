import json
class Led:
	def __init__(self):
		self.x_start = 0
		self.x_end = 0
		self.y_start = 0
		self.y_end = 0
		self.position = 0
		self.color = bytearray([0,0,0])	
		
	def setCoordinates(self, in_x_start, in_x_end, in_y_start,in_y_end):
		self.x_start = in_x_start
		self.x_end = in_x_end
		self.y_start = in_y_start
		self.y_end = in_y_end

	
	def printRaw(self):
		print "led [" , self.position , "] - (" , self.x_start , " , " , self.x_end , ") , Y(", self.y_start , " , " , self.y_end , ")"
	
	def hscan_to_dict(self):
		"""returns dictionary for horizontal coordinates"""
		return dict(minimum =  round(self.x_start,4), maximum = round(self.x_end,4))
	
	def vscan_to_dict(self):
		"""returns dictionary for vertical coordinates"""
		return dict(minimum =  round(self.y_start,4), maximum = round(self.y_end,4))	
	
	def to_json_string(self):
		return json.dumps(self.vscan_to_dict(),sort_keys=False,indent=4, separators=(',', ': '))
	
	def set_color(self,red, green, blue):
		if red > 255 or red < 0 or green > 255 or green < 0 or blue > 255 or blue < 0 :
			raise "Incorrect values (must be between <0,255>"
		else:
			self.color = bytearray([red,green,blue])	

		

class LedChain:
	def __init__(self, no_of_leds):
		self.number_of_leds = no_of_leds
		self.leds = []
		self.offset = 0
		
	def generate_layout(self, nol_horizontal, nol_vertical):
		"""key method in this class - it calculates coordinates of picture scan area. As a result
			there are Led instances created with coordinates assigned"""
		self.nol_horizontal = nol_horizontal
		self.nol_vertical = nol_vertical
		area_top_coordinate = 0.0
		area_bottom_coordinate = 0.0
		area_left_coordinate = 0.0
		area_right_coordinate = 0.0
		
		self.vertical_segment = 1.0/nol_vertical
		self.horizontal_segment = 1.0/nol_horizontal
		for i in range(0,self.number_of_leds):		
			if i < nol_vertical: # right
				vertical_position = i+1
				area_top_coordinate = (1 -(self.vertical_segment * vertical_position))
				area_left_coordinate = 1 - self.horizontal_segment;
			elif i >= nol_vertical and i < nol_vertical + nol_horizontal : #top
				horizontal_position = nol_horizontal - (i - nol_vertical) - 1
				area_left_coordinate = horizontal_position * self.horizontal_segment
				area_top_coordinate = 0.0
			elif i >= nol_vertical + nol_horizontal and i < nol_vertical + nol_horizontal + nol_vertical: #left
				vertical_position = i - nol_vertical - nol_horizontal
				area_top_coordinate = (0 +(self.vertical_segment * vertical_position))
				area_left_coordinate = 0.0
			else: # bottom 
				area_top_coordinate = (1 - self.vertical_segment)
				horizontal_position = i - nol_vertical - nol_horizontal - nol_vertical
				area_left_coordinate = horizontal_position * self.horizontal_segment
		
			area_bottom_coordinate = area_top_coordinate + self.vertical_segment
			area_right_coordinate = area_left_coordinate + self.horizontal_segment
			led = Led()
			led.setCoordinates(area_left_coordinate,area_right_coordinate, area_top_coordinate,area_bottom_coordinate)
			led.position = i
			self.leds.append(led)
		self.original_chain = list(self.leds) #make a copy of initial setup
			
			
	def set_overlap(self,overlap_pct):
		"""Use this method if you want to have leds scanning areas overlaping each other 
			(to loose some details of the effect, to make it smoother"""
		self.horizontal_overlap = (overlap_pct / 100.0) * self.horizontal_segment
		self.vertical_overlap = (overlap_pct / 100.0) * self.vertical_segment
		for led in self.leds:
			led.x_start = max(led.x_start - self.horizontal_overlap,0)
			led.x_end = min(led.x_end + self.horizontal_overlap,1)
			led.y_start = max(led.y_start - self.vertical_overlap,0)
			led.y_end = min(led.y_end + self.vertical_overlap,1)
	
	def reverse_direction(self):
		"""Reverses leds direction from counterclockwise to clockwise""" 
		self.leds.reverse()
	
	def left_bottom_start(self):
		"""Moves the start of leds from right to left bottom corner for clockwise direction"""
	
	def set_offset(self, offset_value):
		"""it can be useful when your leds do not start at right/bottom corner, but, lets say, from the middle of bottom edge"""
		if offset_value > 0:
			for i in range(offset_value):
				self.leds.append(self.leds.pop(0))
		elif offset_value < 0:
			for i in range((-1)*offset_value):
				self.leds.insert(0,self.leds.pop(self.number_of_leds-1))
									
	def print_me(self):
		for i in range(0,len(self.leds)):
			self.leds[i].printRaw()
			
	def to_string(self):
		for i in range(0,len(self.leds)):
			self.leds[i].printRaw()
			
	def leds_to_json_string(self):
		"""Returns json string representing the leds"""
		leds_array = []
		for i in range(0,len(self.leds)):
			leds_array.append(dict(index = i,hscan = self.leds[i].hscan_to_dict(), vscan = self.leds[i].vscan_to_dict()))
		return json.dumps(leds_array,sort_keys=False,indent=4, separators=(',', ': '))
	
	def get_list_of_leds_dicts(self):
		"""Returns array of dicts leds"""
		leds_array = []
		for i in range(0,len(self.leds)):
			leds_array.append(dict(index = i,hscan = self.leds[i].hscan_to_dict(), vscan = self.leds[i].vscan_to_dict()))
		return leds_array	
		
		
	def leds_to_bytearray(self):
		"""Converts leds' colors into bytearray. Useful if you want to send the data to the leds via hyperion interface"""
		data = bytearray()
		for led in self.leds:
			data += led.color
		return data
	
	def set_single_color(self,red,green,blue):
		"""Sets single color for all leds"""
		if red > 255 or red < 0 or green > 255 or green < 0 or blue > 255 or blue < 0 :
			raise "Incorrect values (must be between <0,255>)"
		else:
			for i in range(len(self.leds)):
				self.leds[i].set_color(red, green, blue)		
			
#test
#t = LedChain(50)
#t.set_offset(5)
#t.to_string()
