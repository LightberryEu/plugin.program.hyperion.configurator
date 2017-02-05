import xbmc
import os
import sys
import xbmcaddon
import xbmcgui
import time
import subprocess
import urllib2

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path'))
sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )
new_hyperion_config_path = addon_dir+"/hyperion.config.new"
hyperion_installation_path="/storage/hyperion/bin"
settings_cache_path = "/storage/.kodi/userdata/addon_data/plugin.program.hyperion.configurator/settings.xml"
default_config_path="/storage/.config/hyperion.config.json"
run_command="/storage/hyperion/bin/hyperiond.sh /storage/.kodi/addons/plugin.program.hyperion.configurator-master/hyperion.config.new"
gpio_version=False

import HyperPyCon
import AddonGithubUpdater

line1 = "Welcome!"
line2 = "We are about to prepare your hyperion config file in this step-by-step wizard."
line3 = "You must complete all steps to have the config file generated. Let\'s start!"
xbmcgui.Dialog().ok(addonname, line1, line2 + line3)

try:
    updater=AddonGithubUpdater.AddonGithubUpdater(addon_dir,"LightberryEu","plugin.program.hyperion.configurator")
    if updater.isUpdateAvailable():
        if xbmcgui.Dialog().yesno(addonname, "Plugin update is available. Do you want to install new version?"):
            updater.installUpdate()
            xbmcgui.Dialog().ok(addonname, "Update installed. Please restart plugin")
            sys.exit()
except Exception, e:
    xbmcgui.Dialog().ok(addonname, "Failed to check the update. Maybe your Pi is not connected to the Internet")

#check if hyperion is installed, if not, install the newest version
if not HyperPyCon.HyperPyCon.isHyperionInstalled():
    if HyperPyCon.HyperPyCon.amIonOSMC():
        xbmcgui.Dialog().ok(addonname, "Hyperion installation was not detected. Please install manually...")
        sys.exit()
    xbmcgui.Dialog().ok(addonname, "Hyperion installation was not detected. We will install it now...")
    rc=HyperPyCon.HyperPyCon.install_hyperion()
    if rc==-2 :
        xbmcgui.Dialog().ok(addonname, "Hyperion installation failed. Install script download failed. Please install manually...")
        sys.exit()
    elif rc!=0:
        xbmcgui.Dialog().ok(addonname, "Installation error... Please install manually...")
        sys.exit()


try:
    if HyperPyCon.HyperPyCon.amIonOSMC():
        settings_cache_path = "/home/osmc/.kodi/userdata/addon_data/plugin.program.hyperion.configurator/settings.xml"
        # check if new versio of hyperion is installed
        if os.path.exists("/opt/hyperion/bin/hyperiond"):
            default_config_path="/etc/hyperion.config.json"
        else:
            default_config_path="/etc/hyperion/hyperion.config.json"

        run_command="hyperiond /home/osmc/.kodi/addons/plugin.program.hyperion.configurator-master/hyperion.config.new"
        hyperion_installation_path=""
        subprocess.call(["lsusb"])
        subprocess.call(["killall", "-help"])

except Exception, e:
    if xbmcgui.Dialog().yesno(addonname, "You must have killall and lsusb utilities installed on OSMC. Select Yes to have them installed. No will exit the wizard."):
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Installing...', 'Please wait... it can take few minutes...')
        subprocess.call(["sudo","apt-get","install","-y","psmisc","usbutils"])
        pDialog.close()
    else:
        sys.exit()

try:

    if HyperPyCon.HyperPyCon.amIonWetek() :
        device_versions = [ HyperPyCon.HyperPyCon.adalightapa102 , HyperPyCon.HyperPyCon.adalight , HyperPyCon.HyperPyCon.lightberryXL ]
    else:
        device_versions = [ HyperPyCon.HyperPyCon.adalightapa102 , HyperPyCon.HyperPyCon.adalight,  HyperPyCon.HyperPyCon.ws2801, HyperPyCon.HyperPyCon.apa102, HyperPyCon.HyperPyCon.lightberryXL]
    selected_device = xbmcgui.Dialog().select("Select your led device:",device_versions)
    if selected_device == -1:
        sys.exit();
    if selected_device == 2 or selected_device == 3:
        if "spidev" not in subprocess.check_output(['ls','/dev']):
            xbmcgui.Dialog().ok(addonname, "We have detected that your system does not have spi enabled. You can " +
                                           "still continue, but leds may not work if you're using GPIO/SPI connection")
        gpio_version=True

    if selected_device == 0 or selected_device == 3:
        suffix = "apa102"
    elif selected_device ==4:
        suffix = "xl"
    else:
        suffix = "ws2801"

    xbmcgui.Dialog().ok(addonname, "In next two steps please provide number of leds at the top edge of" +
                        "  tv (horizontally) and number of leds at the side of your tv " +
                        "(count leds at single side only) - horizontally")

    nol_horizontal = xbmcgui.Dialog().input("Select number of leds horizontally","29",xbmcgui.INPUT_NUMERIC)
    nol_vertical = xbmcgui.Dialog().input("Select number of leds vertically","16",xbmcgui.INPUT_NUMERIC)
    if xbmcgui.Dialog().yesno(addonname, "Would you like to download recommended settings for the Lightberry you " +
                                         "selected? WARNING: that will overwrite your current addon settings!"):
        try:
            settingsxml = urllib2.urlopen("http://img.lightberry.eu/download/settings.xml-"+suffix).read()
            f = open(addon_dir+"/resources/settings.xml","w")
            f.write(settingsxml)
            f.close()
            if os.path.isfile(settings_cache_path):
                os.remove(settings_cache_path)
        except Exception, e:
            xbmcgui.Dialog().ok(addonname, repr(e),"Couldnt download the settings - Setup will use default.")
    hyperion_configuration = HyperPyCon.HyperPyCon(int(nol_horizontal), int(nol_vertical), 0.08, 0.1) #parameter from plugin settings to be added
    hyperion_configuration.set_device_type(device_versions[selected_device])
    hyperion_configuration.set_device_rate(int(addon.getSetting("rate")))
    if addon.getSetting("colorOrder") != "Default":
        hyperion_configuration.set_device_color_order(addon.getSetting("colorOrder").lower())

    hyperion_configuration.set_color_values(float(addon.getSetting("redThreshold")), float(addon.getSetting("redGamma")),float(addon.getSetting("redBlacklevel")),float(addon.getSetting("redWhitelevel")),"RED")
    hyperion_configuration.set_color_values(float(addon.getSetting("greenThreshold")), float(addon.getSetting("greenGamma")),float(addon.getSetting("greenBlacklevel")),float(addon.getSetting("greenWhitelevel")),"GREEN")
    hyperion_configuration.set_color_values(float(addon.getSetting("blueThreshold")), float(addon.getSetting("blueGamma")),float(addon.getSetting("blueBlacklevel")),float(addon.getSetting("blueWhitelevel")),"BLUE")
    hyperion_configuration.set_smoothing(addon.getSetting("smoothingType"),int(addon.getSetting("smoothingTime")),int(addon.getSetting("smoothingFreq")))
    hyperion_configuration.set_blackborderdetection((addon.getSetting("bbdEnabled") == "true"), float(addon.getSetting("bbdThreshold")))
    hyperion_configuration.set_grabber_video_standard(addon.getSetting("videoStandard"))
    hyperion_configuration.set_grabber_signal_off(addon.getSetting("colorWhenSourceIsOff"))
    hyperion_configuration.set_grabber_priority(int(float(addon.getSetting("grabberPriority"))))

    options = ["Right/bottom corner and goes up","Left/bottom corner and goes up","Center/bottom and goes right","Center/bottom and goes left"]
    selected_index = xbmcgui.Dialog().select("Select where the led chain starts:",options)

    if selected_index == 1:
        hyperion_configuration.led_chain.reverse_direction()
        hyperion_configuration.led_chain.set_offset(int(nol_horizontal))
    elif selected_index == 2 or selected_index == 3:
        offset = xbmcgui.Dialog().input("How many leds from the center to the corner or the screen?","15",xbmcgui.INPUT_NUMERIC)
        if selected_index == 2:
            hyperion_configuration.led_chain.set_offset((-1)*int(offset))
        else:
            hyperion_configuration.led_chain.reverse_direction()
            hyperion_configuration.led_chain.set_offset(int(offset))

    if gpio_version or device_versions[selected_device] == HyperPyCon.HyperPyCon.lightberryXL:
        # turn off unused leds if this is GPIO version of Lightberry
        hyperion_configuration.disable_extra_leds(150-hyperion_configuration.total_number_of_leds)

    grabber = ""
    if not HyperPyCon.HyperPyCon.amIonWetek():
        lsusb_output = subprocess.check_output('lsusb')
        if "1b71:3002" in lsusb_output:
            grabber = "utv007"
        elif "05e1:0408" in lsusb_output:
            grabber = "stk1160"

        if grabber != "":
            if "video0" in subprocess.check_output(['ls','/dev']):
                if xbmcgui.Dialog().yesno(addonname, "Compatible video grabber has been detected. Do you want to enable video grabber in hyperion?"):
                    hyperion_configuration.config_grabber(grabber)
            else:
                xbmcgui.Dialog().ok(addonname, "Video grabber has been detected but video0 does not exist. Please install drivers or use different disto")
        else:
            xbmcgui.Dialog().ok(addonname, "We have not detected the grabber. Grabber-v4l2 section will not be added to the config file.")

    xbmcgui.Dialog().ok(addonname, "That's all! Now we will attempt to restart hyperion...")
    hyperion_configuration.save_config_file(hyperion_configuration.create_config(),new_hyperion_config_path)
    hyperion_configuration.restart_hyperion(new_hyperion_config_path)

    if not xbmcgui.Dialog().yesno(addonname, "Have you seen the rainbow swirl? (sometimes it does not appear, if you're sure that correct led type is selected, answer YES anyway, save config as default and reboot)"):
        xbmcgui.Dialog().ok(addonname, "Something went wrong... Please try running hyperion from command line to see the error... ("+run_command+")")
        sys.exit()
    else:
        xbmcgui.Dialog().ok(addonname, "For the next 10 seconds you will see test image and leds should adjust to that image. Check if the leds are showing the right colors in the right places."+
            " If not, start this wizard again and provide correct numbers of leds horizontally and vertically.")
        okno = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowId())
        obrazek = xbmcgui.ControlImage(0,0,1280,720,addon_dir+"/test_picture.png")
        okno.addControl(obrazek)
        okno.show()
        obrazek.setVisible(True)
        hyperion_configuration.show_test_image(addon_dir+"/test_picture.png")
        time.sleep(10)
        okno.close()
        hyperion_configuration.clear_leds()

    if xbmcgui.Dialog().yesno(addonname, "Do you want to save this config as your default one?","(if No, changes will be lost after hyperion/system restart)"):
        hyperion_configuration.overwrite_default_config()
    elif xbmcgui.Dialog().yesno(addonname, "Hyperion is now running with the newly created config. Would you like to restart hyperion with previous config?"):
        hyperion_configuration.restart_hyperion(default_config_path)

    xbmcgui.Dialog().ok(addonname, "That\'s all Folks! :) . Enjoy!", "If you'd like to fine tune advanced parameters, please modify addon settings before running it","You may need to restart your system...")

except Exception, e:
        xbmcgui.Dialog().ok(addonname, repr(e),"Please report an error at github issue list")


