import urllib2
import subprocess
import xbmcgui

class AddonGithubUpdater:
	def __init__(self, addonParentFolder, addonFolderName, githubOrg, githubRepo):
		self.githubOrg=githubOrg
		self.githubRepo=githubRepo
		self.addonParentFolder=addonParentFolder
		self.addonFolderName=addonFolderName

	
	def isUpdateAvailable(self):
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('Updater..', 'Please wait... Checking for updates...')		
		f=open(self.addonParentFolder+"/"+self.addonFolderName+"/changelog.txt")
		local=f.readlines()[-1]
		f.close()
		remote=urllib2.urlopen("https://raw.githubusercontent.com/LightberryEu/plugin.program.hyperion.configurator/master/changelog.txt").readlines()[-1]
		pDialog.close()
		#xbmcgui.Dialog().ok("test", local, remote)
		return local!=remote
		
	def installUpdate(self):
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('Updater..', 'Please wait... Installing update...')
		f=open("/storage/downloads/update_plugin.zip","w")
		f.write(urllib2.urlopen("https://github.com/"+self.githubOrg+"/"+self.githubRepo+"/archive/master.zip").read())
		f.close()
		subprocess.call(["unzip","-o","/storage/downloads/update_plugin.zip","-d",self.addonParentFolder])
		pDialog.close()

if __name__ == "__main__":
	updater=AddonGithubUpdater("/storage/.kodi/addons","plugin.program.hyperion.configurator-master","LightberryEu","plugin.program.hyperion.configurator")
	if updater.isUpdateAvailable():
		print "update available"
		updater.installUpdate()
		print "plugin installed"
		
		
