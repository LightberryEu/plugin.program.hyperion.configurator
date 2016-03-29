import json
from collections import OrderedDict

blackborderdetectord = dict(enable = True, threshold = 0.05)
effectsd = dict(paths = ["/storage/hyperion/effects"])
bootsequenced = dict(effect = "Rainbow swirl fast", duration_ms = 3000)
framegrabberd = dict(width = 64, height = 64, frequency_Hz = 10.0)
amlgrabberd = dict(width = 64, height = 64, frequency_Hz = 20.0)
json_serverd = dict(port = 19444)
proto_serverd = dict(port = 19445)

class Device:
	name = "MyPi"
	type = "ws2801"
	output = "/dev/spidev0.0"
	rate = 500000
	color_order = "rgb"

	def __init__(self):
		self.name = "MyPi"
		self.type = "ws2801"
		self.output = "/dev/spidev0.0"
		self.rate = 500000
		self.color_order = "rgb"

	def to_dict(self):
		return OrderedDict(name = self.name, type = self.type, output = self.output, rate = self.rate, colorOrder = self.color_order)


class SingleColor:
	threshold = 0.0700
	gamma = 2.0000
	blacklevel = 0.0000
	whitelevel = 1.0000

	def __init__(self,threshold,gamma,blacklevel,whitelevel):
		self.threshold = threshold
		self.gamma = gamma
		self.blacklevel = blacklevel
		self.whitelevel = whitelevel

	def to_dict(self):
		return OrderedDict(threshold = self.threshold, gamma = self.gamma, blacklevel = self.blacklevel, whitelevel = self.whitelevel)

class HSV:
	saturation_gain = 1.0000
	value_gain = 1.0000

	def __init__(self,saturation_gain,value_gain):
		self.saturation_gain = saturation_gain
		self.value_gain = value_gain

	def to_dict(self):
		return OrderedDict(saturationGain = self.saturation_gain, valueGain = self.value_gain )

class Transform:
	tranformation_id = "default"
	leds_indexes_range = "*"
	red = None
	green = None
	blue = None
	hsv = None

	def __init__(self,tranformation_id, leds_indexes_range, hsv, red, green, blue):
		"""red,green,blue must be instances of SingleColorParms"""
		self.tranformation_id = tranformation_id
		self.leds_indexes_range = leds_indexes_range
		self.red = red
		self.green = green
		self.blue = blue
		self.hsv = hsv

	def to_dict(self):
		return OrderedDict(id = self.tranformation_id, leds = self.leds_indexes_range, hsv = self.hsv.to_dict(), red = self.red.to_dict(), green = self.green.to_dict(), blue = self.blue.to_dict())
		
	def set_color_transformation(self, single_color_settings, color_name):
		if color_name == "GREEN":
			self.green = single_color_settings
		elif color_name == "RED":
			self.red = single_color_settings
		else:	
			self.blue = single_color_settings
			

class Smoothing:
	type = 'linear'
	time_ms = 100
	update_frequency = 20.0000

	def __init__(self,type,time_ms,update_frequency):
		self.type = type
		self.time_ms = time_ms
		self.update_frequency = update_frequency

	def to_dict(self):
		return OrderedDict(type = self.type,time_ms = self.time_ms,updateFrequency = self.update_frequency)

class Color:
	transformations = []
	smoothing = None

	def __init__(self):
		self.transformations = []
		pass

	def add_transformation(self, transformation):
		self.transformations.append(transformation.to_dict())

	def set_smoothing(self, smoothing):
		self.smoothing = smoothing

	def to_dict(self):
		return OrderedDict(transform = self.transformations,smoothing = self.smoothing.to_dict())

class BootSequence:
	def __init__(self):
		self.effect = "Rainbow swirl fast"
		self.duration_ms = 1000

	def to_dict(self):
		return OrderedDict(effect = self.effect, duration_ms = self.duration_ms)

class XBMCVideoChecker:
	def __init__(self):
		self.xbmc_address = "127.0.0.1"
		self.xbmc_tcp_port = 9090
		self.grab_video = True
		self.grab_pictures = True
		self.grab_audio = True
		self.grab_menu = False
		self.grab_screensaver = True
		self.enable_3D_detection = True

	def to_dict(self):
		return dict(xbmcAddress = self.xbmc_address, xbmcTcpPort = self.xbmc_tcp_port, grabVideo = self.grab_video, grabPictures = self.grab_pictures, 
			grabAudio = self.grab_audio, grabMenu = self.grab_menu, grabScreensaver = self.grab_screensaver, enable3DDetection = self.enable_3D_detection)

class GrabberV4l2:
	def __init__(self):
		self.device = "/dev/video0"
		self.input = 0
		self.standard = "PAL"
		self.width = 720
		self.height = 576
		self.frame_decimation = 2
		self.size_decimation = 8
		self.priority = 900
		self.mode = "2D"
		self.crop_left = 5
		self.crop_right = 5
		self.crop_top = 5
		self.crop_bottom = 5
		self.red_signal_threshold = 0.2
		self.green_signal_threshold = 0.2
		self.blue_signal_threshold = 0.2

	def to_dict(self):
		return OrderedDict(
			device = self.device,
			input = self.input,
			standard = self.standard,
			width = self.width,
			height = self.height,
			frameDecimation = self.frame_decimation,
			sizeDecimation = self.size_decimation,
			priority = self.priority,
			mode = self.mode,
			cropLeft = self.crop_left,
			cropRight = self.crop_right,
			cropTop = self.crop_top,
			cropBottom = self.crop_bottom,
			redSignalThreshold = self.red_signal_threshold,
			greenSignalThreshold = self.green_signal_threshold,
			blueSignalThreshold = self.blue_signal_threshold
			)









