from sys import argv
import time, subprocess
from collections import OrderedDict
from Led import Led, LedChain
import HyperionConfigTester
import HyperionConfigSections
import sys
import json

nol_horizontal = int(argv[1])
nol_vertical = int(argv[2])
h_depth = int(argv[3])
v_depth = int(argv[4])
#index of the led in right bottom corner
offset = int(argv[5])

total_number_of_leds = ((nol_horizontal + nol_vertical) * 2)
print "Arguments are"
print "Number of horizontal leds: " , nol_horizontal
print "Number of vertical leds: " , nol_vertical
print "Horizontal depth: " , h_depth
print "Vertical depth: " , v_depth
print total_number_of_leds

led_chain = LedChain(total_number_of_leds)
led_chain.generate_layout(nol_horizontal, nol_vertical)
led_chain.to_string()
print "proba"
print led_chain.leds_to_json_string()


transform = HyperionConfigSections.Transform("idd","0-89", 
	HyperionConfigSections.HSV(1.0,1.0),
	HyperionConfigSections.SingleColor(0.05,2.2,0,1),
	HyperionConfigSections.SingleColor(0.05,2.0,0,0.85),
	HyperionConfigSections.SingleColor(0.05,2.0,0,0.85))	
	
	
color = HyperionConfigSections.Color()
color.add_transformation(transform)
color.define_smoothing(HyperionConfigSections.Smoothing("linear",100,20))
hyperion_config_dict = OrderedDict(
	device = HyperionConfigSections.Device().to_dict(), 
	color = color.to_dict(), 
	leds = led_chain.get_list_of_leds_dicts(),
	blackborderdetector = HyperionConfigSections.blackborderdetectord, 
	effects = HyperionConfigSections.effectsd, 
	bootsequence = HyperionConfigSections.bootsequenced,
	framegrabber = HyperionConfigSections.framegrabberd, 
	xbmcVideoChecker = HyperionConfigSections.XBMCVideoChecker().to_dict(), 
# 	grabber_v4l2 = GrabberV4l2().to_dict(), 
	jsonServer = HyperionConfigSections.json_serverd, 
	protoServer = HyperionConfigSections.proto_serverd, 
	endOfJson = 'endOfJson')
print json.dumps(hyperion_config_dict,sort_keys=False,indent=4, separators=(',', ': '))	
f = open("nowy_konfig.json","w", 0777)
f.write(json.dumps(hyperion_config_dict,sort_keys=False,indent=4, separators=(',', ': ')))
f.close()
print "koniec"
#try:
	#hyperion_config_file = open('hyperion.config.json_new','w')
	#part1 = open('hyperion.config.json_part1','r')
	#part2 = open('hyperion.config.json_part2','r')
	#last_part = open('hyperion.config.json_lastpart','r')
	#hyperion_config_file.write(part1.read())
	#hyperion_config_file.write(led_chain.leds_to_json_string())
	#hyperion_config_file.write(part2.read())

	##appending grabber-v4l2 section 
	#if "1b71:3002" in subprocess.check_output('lsusb'):
		#grabber_part = open('hyperion.config.json_grabberutv007','r')
		#hyperion_config_file.write(grabber_part.read())
		#grabber_part.close()
	#hyperion_config_file.write(last_part.read())
	#hyperion_config_file.close()
	#part1.close()
	#part2.close()
	#last_part.close()
#except NameError as e:
	#print e.args	
#except:
	#print "read/write error occured:", sys.exc_info()[0]
	#exit
	
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



