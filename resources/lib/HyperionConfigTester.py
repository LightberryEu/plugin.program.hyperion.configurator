from json_client import JsonClient
import subprocess
import os

class HyperionConfigTester:
	connection = None
	hyperion_path = ""
	config_folder = ""
	led_chain = None
	def __init__(self, chain = None):
		self.led_chain = chain
		#if os.uname()[1] == "OpenELEC":
		if os.path.isdir("/storage/.config"):
			self.hyperion_path = "/storage/hyperion/bin/hyperiond.sh"
			self.config_folder = "/storage/.config/"
			self.hyperion_remote_path = "/storage/hyperion/bin/hyperion-remote.sh"
		else: #not tested
			self.hyperion_path = "hyperiond"
			self.config_folder = "/etc/"
			self.hyperion_remote_path = "hyperion-remote"

	def restart_hyperion(self,config_file_name):
		subprocess.call(["killall", "hyperiond"])
		subprocess.Popen([self.hyperion_path, self.config_folder+config_file_name])

	def connect_to_hyperion(self):	
		"""Connects to local hyperion"""
		self.connection = JsonClient('127.0.0.1', 19444, timeout=10)
		self.connection.connect()

	def mark_corners(self):
		self.led_chain.leds[self.led_chain.nol_vertical].set_color(255,0,0)
		self.led_chain.leds[self.led_chain.nol_vertical+self.led_chain.nol_horizontal].set_color(0,255,0)
		self.led_chain.leds[(self.led_chain.nol_vertical*2)+self.led_chain.nol_horizontal].set_color(0,0,255)

	def change_colors(self):
		self.connection.send_led_data(self.led_chain.leds_to_bytearray())

	def set_single_color(self, red, green, blue):
		self.led_chain.set_single_color(red, green, blue)

	def disconnect(self):
		self.connection.disconnect()

	def show_test_image(self, test_image_path):
		 subprocess.Popen([self.hyperion_remote_path,"-i", test_image_path])

	def clear_leds(self):
		subprocess.Popen([self.hyperion_remote_path,"-c", "000000"])
