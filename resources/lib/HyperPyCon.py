from sys import argv
import time, subprocess
from collections import OrderedDict
from Led import Led, LedChain
import HyperionConfigTester
import HyperionConfigSections
import sys
import json
import os
import shutil

class HyperPyCon:
	ws2801 = "Lightberry for Raspberry Pi"
	adalight = "Lightberry USB"
	apa102 = "Lightberry HD APA"
	def __init__(self, nol_horizontal, nol_vertical):
		self.total_number_of_leds = ((nol_horizontal + nol_vertical) * 2)
		self.led_chain = LedChain(self.total_number_of_leds)
		self.led_chain.generate_layout(nol_horizontal, nol_vertical)
		self.transform = HyperionConfigSections.Transform("leds","0-"+str(self.total_number_of_leds-1),
			HyperionConfigSections.HSV(1.0,1.0),
			HyperionConfigSections.SingleColor(0.05,2.2,0,1),
			HyperionConfigSections.SingleColor(0.05,2.0,0,0.85),
			HyperionConfigSections.SingleColor(0.05,2.0,0,0.85))
		self.color = HyperionConfigSections.Color()
		self.smoothing = HyperionConfigSections.Smoothing("linear",100,20)
		self.device = HyperionConfigSections.Device()
		self.blackborderdetector = HyperionConfigSections.blackborderdetectord
		self.effects = HyperionConfigSections.effectsd
		self.bootsequence = HyperionConfigSections.bootsequenced
		self.framegrabber = HyperionConfigSections.framegrabberd
		self.xbmcVideoChecker = HyperionConfigSections.XBMCVideoChecker()
		self.jsonServer = HyperionConfigSections.json_serverd
		self.protoServer = HyperionConfigSections.proto_serverd
		self.grabber = HyperionConfigSections.GrabberV4l2()

		self.tester = HyperionConfigTester.HyperionConfigTester(self.led_chain)

	def set_device_type(self,device_type):
		if device_type == HyperPyCon.adalight:
			self.device.type = "adalight"
			self.device.output = "/dev/ttyACM0"
		elif device_type == HyperPyCon.apa102:
			self.device.type = "apa102"
			
	def set_device_rate(self, rate):
		self.device.rate = rate
		
	def set_color_values(self,threshold, gamma, blacklevel,whitelevel, color_name):
		self.transform.set_color_transformation(HyperionConfigSections.SingleColor(threshold,gamma,blacklevel,whitelevel), color_name)
		
	def set_smoothing(self, type, time_ms, update_frequency):
		self.smoothing = HyperionConfigSections.Smoothing(type,time_ms,update_frequency)
		
	def set_blackborderdetection(self,enabled,bbdthreshold):
		self.blackborderdetector = dict(enable = enabled, threshold = bbdthreshold)

	def create_config(self, add_grabber):
		self.color.add_transformation(self.transform)
		self.color.set_smoothing(self.smoothing)
		hyperion_config_dict = OrderedDict(
			device = self.device.to_dict(), 
			color = self.color.to_dict(), 
			leds = self.led_chain.get_list_of_leds_dicts(),
			blackborderdetector = self.blackborderdetector, 
			effects = self.effects, 
			bootsequence = self.bootsequence,
			framegrabber = self.framegrabber, 
			xbmcVideoChecker = self.xbmcVideoChecker.to_dict(), 
			jsonServer = self.jsonServer, 
			protoServer = self.protoServer, 
			endOfJson = 'endOfJson')

		if add_grabber:
			hyperion_config_dict.update(OrderedDict(grabber_v4l2 = HyperionConfigSections.GrabberV4l2().to_dict()))

		return json.dumps(hyperion_config_dict,sort_keys=False,indent=4, separators=(',', ': ')).replace("grabber_v4l2","grabber-v4l2")

	def save_config_file(self,content,folder,file_name):
		self.config_file_path = folder+file_name
		f = open(folder+file_name,"w", 0777)
		f.write(content)
		f.close()

	def overwrite_default_config(self):
		if os.path.isdir("/storage/.config"):
			config_folder = "/storage/.config/"
		else:
			config_folder = "/etc/"

		shutil.copyfile(config_folder+"hyperion.config.json",config_folder+"hyperion.config.json_bak")
		shutil.copyfile(self.config_file_path,config_folder+"hyperion.config.json")

	def config_grabber(self,grabber_model):
		"""setting grabber specific parameters. utv007 model is default"""
		if grabber_model == "stk1160":
			self.grabber.width = 240
			self.grabber.height = 192
			self.grabber.frame_decimation = 2
			self.grabber.size_decimation = 20

	def restart_hyperion(self,hyperion_config_file_name):
		self.tester.restart_hyperion(hyperion_config_file_name)

	def test_corners(self,duration):
		self.tester.connect_to_hyperion()
		self.tester.mark_corners()
		self.tester.change_colors()
		time.sleep(duration)
		self.tester.disconnect()

	def show_test_image(self, image_path):
		self.tester.show_test_image(image_path)

	def clear_leds(self):
		self.tester.clear_leds()		


#h = HyperPyCon(23,23)
#h.restart_hyperion()	
#print "Config ready"
#print "Testing leds..."
#test = HyperionConfigTester.HyperionConfigTester(led_chain, "OPENELEC")
#test.connect_to_hyperion()
#test.mark_corners()
##test.change_colors()
##time.sleep(5)
#test.set_single_color(255,255,0)
##test.change_colors()
##time.sleep(5)
#test.disconnect();

#print json.dumps(hyperion_dict_templates.GrabberV4l2.to_dict())



