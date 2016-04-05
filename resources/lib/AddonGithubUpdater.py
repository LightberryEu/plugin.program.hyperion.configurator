import urllib2
import subprocess
import xbmcgui
import os

class AddonGithubUpdater:
	def __init__(self, addonFolderName, githubOrg, githubRepo):
		self.githubOrg=githubOrg
		self.githubRepo=githubRepo
		self.addonParentFolder=os.path.split(addonFolderName)[0]
		self.addonFolderName=os.path.split(addonFolderName)[1]
		self.addonFullPath=addonFolderName

	
	def isUpdateAvailable(self):
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('Updater..', 'Please wait... Checking for updates...')		
		f=open(self.addonFullPath+"/changelog.txt")
		local=f.readlines()[-1]
		f.close()
		remote=urllib2.urlopen("https://raw.githubusercontent.com/LightberryEu/plugin.program.hyperion.configurator/master/changelog.txt").readlines()[-1]
		pDialog.close()
		#xbmcgui.Dialog().ok("test", local, remote)
		return local!=remote
		
	def installUpdate(self):
		download_path=os.path.expanduser("~/update_plugin.zip")
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('Updater..', 'Please wait... Installing update...')
		f=open(download_path,"w")
		f.write(urllib2.urlopen("https://github.com/"+self.githubOrg+"/"+self.githubRepo+"/archive/master.zip").read())
		f.close()
		subprocess.call(["unzip","-o",download_path,"-d",self.addonParentFolder])
		pDialog.close()

		
		
