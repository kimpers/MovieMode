#!/usr/bin/python

# MovieMode.py
# Inhibits screensaver and kills screen colorization application like redshift when the active window
# has a certain name, perfect for watching movies or playing games. When application window no longer
# is the active screensaver and colorization application are restorned to normal.
# Program prints active window in console so it's easy to see what to put in config file
# Author: Kim

import subprocess
import dbus
import os
import time
import re

from Xlib.display import Display
from Xlib import X, error
from ConfigParser import SafeConfigParser

class MovieMode:
	def __init__(self):
		self.sleepIsPrevented = False
		self.redshiftIsKilled = False
		parser = SafeConfigParser()
		parser.read('config.cfg')
		self.windows = [w.strip() for w in parser.get('applications', 'window_identifiers').split(',')]
		self.refreshRate = int(parser.get('other', 'refresh_rate').strip())

	def toggleScreenSaver(self):
		bus = dbus.SessionBus()
		proxy = bus.get_object ('org.gnome.SessionManager', '/org/gnome/SessionManager')
		sessionManager = dbus.Interface (proxy, 'org.gnome.SessionManager')
		if self.sleepIsPrevented:
			if self.screenSaverCookie != None:
				print("Uninhibiting screensaver")
				sessionManager.Uninhibit(self.screenSaverCookie)
		else:
			print("Inhibiting screensaver")
			self.screenSaverCookie = sessionManager.Inhibit ("MovieMode.py", 0, "Screensaver inhibit movie mode", 8)
		self.sleepIsPrevented = not self.sleepIsPrevented

	def toggleRedshift(self):
		print("Toggle redshift")
		subprocess.Popen('pkill -USR1 redshift', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	def checkXSession(self):
		try:
			self.display.no_operation()
			self.display.sync()
		except error.ConnectionClosedError:
			return False
		return True
	def getActiveWindow(self):
		#If no xsession we return None
		if self.checkXSession() == None:
			return None
		ret = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType)
		if ret is not None:
			windowID = ret.value[0]
			if windowID != 0:
				window = self.display.create_resource_object('window', windowID)
				winclass = window.get_wm_class()
				print 'Active Window: ', winclass[1]
				return winclass[1]
		else:
			print("No active window")
			return None

	# Checks every X seconds if active window is any of the specified windows
	def start(self):
		self.display = Display()
		self.root = self.display.screen().root
		disabled = False
		while(True):
			window = self.getActiveWindow()
			if window != None:
				matchedWindow = any(w in window for w in self.windows)
				if matchedWindow and not disabled or not matchedWindow and disabled:
					self.toggleScreenSaver()
					self.toggleRedshift()
					disabled = not disabled
				else:
					print("Do nothing")
			print("Sleeping...")
			time.sleep(self.refreshRate)

if __name__ == "__main__":
		m = MovieMode()
		m.start()
