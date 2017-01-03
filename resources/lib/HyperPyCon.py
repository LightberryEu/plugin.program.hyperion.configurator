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
    ws2801 = "Lightberry HD for Raspberry Pi (ws2801)"
    apa102 = "Lightberry HD for Raspberry Pi (apa102)"
    adalight = "Lightberry HD USB (ws2801)"
    adalightapa102 = "Lightberry HD USB (apa102)"
    lightberryXL = "Lightberry XL"
    qty_of_disabled_leds=0

    def __init__(self, nol_horizontal, nol_vertical,horizontal_depth, vertical_depth):
        self.grabber_enabled = False
        self.total_number_of_leds = ((nol_horizontal + nol_vertical) * 2)
        self.led_chain = LedChain(self.total_number_of_leds)
        self.led_chain.generate_layout(nol_horizontal, nol_vertical,horizontal_depth, vertical_depth)
        self.transform = HyperionConfigSections.Transform("leds","0-"+str(self.total_number_of_leds-1),
            HyperionConfigSections.HSV(1.0,1.0),
            HyperionConfigSections.SingleColor(0.05,2.2,0,1),
            HyperionConfigSections.SingleColor(0.05,2.0,0,0.85),
            HyperionConfigSections.SingleColor(0.05,2.0,0,0.85))
        self.color = HyperionConfigSections.Color()
        self.smoothing = HyperionConfigSections.Smoothing("linear",100,20)
        self.device = HyperionConfigSections.Device()
        self.blackborderdetector = HyperionConfigSections.blackborderdetectord
        if HyperPyCon.amIonOSMC():
            self.effects = dict(paths = ["/opt/hyperion/effects"])
        else:
            self.effects = HyperionConfigSections.effectsd
        self.bootsequence = HyperionConfigSections.bootsequenced
        if HyperPyCon.amIonWetek():
            self.amlgrabber = HyperionConfigSections.amlgrabberd
        else:
            self.framegrabber = HyperionConfigSections.framegrabberd
            self.grabber = HyperionConfigSections.GrabberV4l2()
        self.xbmcVideoChecker = HyperionConfigSections.XBMCVideoChecker()
        self.jsonServer = HyperionConfigSections.json_serverd
        self.protoServer = HyperionConfigSections.proto_serverd

        self.tester = HyperionConfigTester.HyperionConfigTester(self.led_chain)

    @staticmethod
    def amIonWetek():
        if "Amlogic" in open("/proc/cpuinfo").read():
            return True
        else:
            return False

    @staticmethod
    def amIonOSMC():
                if "osmc" in open("/proc/version").read():
                        return True
                else:
                        return False

    @staticmethod
    def isHyperionInstalled():
        if os.path.isdir("/storage/hyperion/bin") or os.path.isdir("/opt/hyperion") or os.path.isdir("/usr/share/hyperion"):
            return True
        else:
            return False

    @staticmethod
    def install_hyperion():
        if HyperPyCon.amIonOSMC():
            return -1
        rc=subprocess.call(["curl","-L","--output","/storage/install_hyperion.sh","--get","https://raw.githubusercontent.com/tvdzwan/hyperion/master/bin/install_hyperion.sh"])
        if rc!=0:
            return -2
        return subprocess.call(["sh", "/storage/install_hyperion.sh"])

    def set_device_type(self,device_type):
        if device_type == HyperPyCon.adalight or device_type == HyperPyCon.lightberryXL:
            self.device.type = "adalight"
            self.device.output = "/dev/ttyACM0"
        elif device_type == HyperPyCon.apa102:
            self.device.type = "apa102"
            self.device.color_order = "bgr"
        elif device_type == HyperPyCon.adalightapa102:
            self.device.type = "adalightapa102"
            self.device.output = "/dev/ttyACM0"
            self.device.color_order = "bgr"

    def set_device_rate(self, rate):
        self.device.rate = rate

    def set_device_color_order(self, colorOrder):
        self.device.color_order = colorOrder

    def set_color_values(self,threshold, gamma, blacklevel,whitelevel, color_name):
        self.transform.set_color_transformation(HyperionConfigSections.SingleColor(threshold,gamma,blacklevel,whitelevel), color_name)

    def set_smoothing(self, type, time_ms, update_frequency):
        self.smoothing = HyperionConfigSections.Smoothing(type,time_ms,update_frequency)

    def set_blackborderdetection(self,enabled,bbdthreshold):
        self.blackborderdetector = dict(enable = enabled, threshold = bbdthreshold)

    def create_config(self):
        self.color.add_transformation(self.transform)
        if self.qty_of_disabled_leds != 0:
            self.color.add_transformation(self.ledsoff_transform)
        self.color.set_smoothing(self.smoothing)
        if HyperPyCon.amIonWetek():
            hyperion_config_dict = OrderedDict(
                device = self.device.to_dict(),
                color = self.color.to_dict(),
                leds = self.led_chain.get_list_of_leds_dicts(),
                blackborderdetector = self.blackborderdetector,
                effects = self.effects,
                bootsequence = self.bootsequence,
                amlgrabber = self.amlgrabber,
                xbmcVideoChecker = self.xbmcVideoChecker.to_dict(),
                jsonServer = self.jsonServer,
                protoServer = self.protoServer,
                endOfJson = 'endOfJson')
        else:
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

        if self.grabber_enabled:
            hyperion_config_dict.update(OrderedDict(grabber_v4l2 = self.grabber.to_dict()))

        return json.dumps(hyperion_config_dict,sort_keys=False,indent=4, separators=(',', ': ')).replace("grabber_v4l2","grabber-v4l2")

    def save_config_file(self,content,file_path):
        self.config_file_path = file_path
        f = open(file_path,"w", 0777)
        f.write(content)
        f.close()

    def overwrite_default_config(self):
        if os.path.isdir("/storage/.config"):
            config_folder = "/storage/.config/"
        else:
            config_folder = "/etc/"

        if HyperPyCon.amIonOSMC():
            subprocess.call(["sudo","cp",config_folder+"hyperion.config.json",config_folder+"hyperion.config.json_bak"])
            subprocess.call(["sudo","cp",self.new_hyperion_config_path,config_folder+"hyperion.config.json"])
        else:
            shutil.copyfile(config_folder+"hyperion.config.json",config_folder+"hyperion.config.json_bak")
            shutil.copyfile(self.new_hyperion_config_path,config_folder+"hyperion.config.json")

    def config_grabber(self,grabber_model):
        self.grabber_enabled = True
        """setting grabber specific parameters. utv007 model is default"""
        if grabber_model == "stk1160":
            self.grabber.width = 180
            if self.grabber.standard == "PAL":
                self.grabber.height = 144
            else:
                self.grabber.height = 120
            self.grabber.frame_decimation = 2
            self.grabber.size_decimation = 2
        else:
            self.grabber.width = 720
            if self.grabber.standard == "PAL":
                self.grabber.height = 576
            else:
                self.grabber.height = 480
            self.grabber.frame_decimation = 2
            self.grabber.size_decimation = 8

    def restart_hyperion(self,hyperion_config_path):
        self.new_hyperion_config_path = hyperion_config_path
        self.tester.restart_hyperion(hyperion_config_path)

    def test_corners(self,duration):
        self.tester.connect_to_hyperion()
        self.tester.mark_corners()
        self.tester.change_colors()
        time.sleep(duration)
        self.tester.disconnect()

    def show_test_image(self, image_path):
        self.tester.show_test_image(image_path)

    def set_grabber_video_standard(self,standard):
        self.grabber.standard = standard;

    def set_grabber_signal_off(self,color_when_off):
        if(color_when_off == "BLUE"):
            self.grabber.red_signal_threshold = 0.1
            self.grabber.green_signal_threshold = 0.1
            self.grabber.blue_signal_threshold = 1.0

    def clear_leds(self):
        self.tester.clear_leds()

    def disable_extra_leds(self, qty_of_disabled_leds):
        self.qty_of_disabled_leds=qty_of_disabled_leds
        self.ledsoff_transform = HyperionConfigSections.Transform("ledsOff",str(self.total_number_of_leds)+"-"+str(self.total_number_of_leds+self.qty_of_disabled_leds-1),
            HyperionConfigSections.HSV(0,0),
            HyperionConfigSections.SingleColor(0.05,2.2,0,0),
            HyperionConfigSections.SingleColor(0.05,2.0,0,0),
            HyperionConfigSections.SingleColor(0.05,2.0,0,0))
        self.led_chain.add_extra_leds(qty_of_disabled_leds)


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



