import xbmc
import os
import sys
import xbmcaddon
import xbmcgui
import time
import subprocess

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )
sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )
import HyperPyCon 

line1 = "Welcome!"
line2 = "We are about to prepare your hyperion config file in this step-by-step wizard."
line3 = "You must complete all steps to have the config file generated. Let\'s start!"

xbmcgui.Dialog().ok(addonname, line1, line2 + line3)

try:
	if "spidev" not in subprocess.check_output(['ls','/dev']):
		xbmcgui.Dialog().ok(addonname, "We have detected that your system does not have spi enabled. You can still continue, but leds may not work if you're using GPIO/SPI connection."+
			" For USB connection you are safe to proceed")

	xbmcgui.Dialog().ok(addonname, "In next two steps please provovide number of leds at the top edge of tv (horizontally)" +
		"  and number of leds at the side of your tv (count leds at single side only) - horizontally")

	nol_horizontal = xbmcgui.Dialog().input("Select number of leds horizontally","16",xbmcgui.INPUT_NUMERIC)
	nol_vertical = xbmcgui.Dialog().input("Select number of leds vertically","9",xbmcgui.INPUT_NUMERIC)

	hyperion_configuration = HyperPyCon.HyperPyCon(int(nol_horizontal), int(nol_vertical))

	options = ["Right bottom corner and goes up","Left bottom corner and goes up"]
	selected_index = xbmcgui.Dialog().select("Select where the led chain starts:",options)

	if options[selected_index] == "Left bottom corner and goes up":
		hyperion_configuration.led_chain.reverse_direction()
		hyperion_configuration.led_chain.set_offset(int(nol_horizontal))

	grabber = ""
	lsusb_output = subprocess.check_output('lsusb')

	if "1b71:3002" in lsusb_output:
		grabber = "utv007"
	elif "05e1:0408" in lsusb_output:
		grabber = "stk1160"

	if grabber != "":
		if "video0" in subprocess.check_output(['ls','/dev']):
			xbmcgui.Dialog().ok(addonname, "Compatible video grabber has been detected. We will add appropriate section to the config file.")
			hyperion_configuration.config_grabber(grabber)
		else:
			xbmcgui.Dialog().ok(addonname, "Video grabber has been detected but video0 does not exist. Please install drivers or use different disto")
	else:
		xbmcgui.Dialog().ok(addonname, "We have not detected the grabber. Grabber-v4l2 section will not be added to the config file.")

	xbmcgui.Dialog().ok(addonname, "That's all! Now we will attempt to restart hyperion...")
	hyperion_configuration.save_config_file(hyperion_configuration.create_config(grabber),"/storage/.config/","hyperion.config.new")
	hyperion_configuration.restart_hyperion("hyperion.config.new")
	if not xbmcgui.Dialog().yesno(addonname, "Have you seen the rainbow swirl?"):
		xbmcgui.Dialog().ok(addonname, "Something went wrong... Please try running hyperion from command line to see the error...")
		sys.exit()
	else:
		xbmcgui.Dialog().ok(addonname, "For the next 10 seconds you will see leds in 3 corners marked with different colors. Check if they are exactly in the corners."+
			" If not, start this wizard again and provide correct numbers of leds horizontally and vertically.")
		hyperion_configuration.test_corners(10)

	if xbmcgui.Dialog().yesno(addonname, "Do you want us to save this config as your default one?","(if No, changes will be lost after hyperion/system restart)"):
		hyperion_configuration.overwrite_default_config()
	elif xbmcgui.Dialog().yesno(addonname, "Hyperion is now running with the newly created config. Would you like to restart hyperion with previous config?"):
		hyperion_configuration.restart_hyperion("hyperion.config.json")

	xbmcgui.Dialog().ok(addonname, "That\'s all Folks! :) . Enjoy!")

except Exception, e:
        xbmcgui.Dialog().ok(addonname, repr(e))


