#!/usr/bin/python
import subprocess, dbus,os, time,re
from Xlib.display import Display
from Xlib import X, error
from ConfigParser import SafeConfigParser
class MovieMode:
	def __init__(self):
		self.sleepIsPrevented = False
		self.redshiftIsKilled = False
		parser = SafeConfigParser()
		parser.read('config.cfg')
		self.matches = [w.strip() for w in parser.get('applications','process_identifiers').split(',')]
		self.windows = [w.strip() for w in parser.get('applications', 'window_identifiers').split(',')]
		self.colorApp = parser.get('other', 'screen_colorization_application').strip()
		self.refreshRate = int(parser.get('other', 'refresh_rate').strip())
	def processesRunning(self):
		p = subprocess.Popen('ps -ef', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in p.stdout.readlines():
			if any(m in line for m in self.matches):
				print "Matched line: " + line
				return True
		return False

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
		if self.redshiftIsKilled:
			print("Restarting redshift")
			subprocess.Popen('redshift &', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			self.redshiftIsKilled = False
		else:
			p = subprocess.Popen('ps -ef', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			for line in p.stdout.readlines():
				if self.colorApp in line:
					print("matched " + self.colorApp + " on line " + line)
					matches = re.findall(r"\d{2,}",line)
					if matches:
						# kill the pid of redshift
						print("killing " + self.colorApp + " on pid " + matches[0])
						subprocess.Popen('kill ' + matches[0], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
						self.redshiftIsKilled = True
						break
					else:
						print("Could not find PID for colorization application")
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
				title = window.get_wm_name()
				winclass = window.get_wm_class()
				print 'Active Window: ', winclass
				return winclass
		else:
			print("No active window")
			return None
	def start(self):
		self.display = Display()
		self.root = self.display.screen().root
		disabled = False
		while(True):
			window = self.getActiveWindow()
			matchedWindow = any(w in window for w in self.windows)
			isRunning = self.processesRunning()
			if matchedWindow and isRunning and not disabled or not matchedWindow and disabled:
				self.toggleScreenSaver()
				self.toggleRedshift()
				disabled = not disabled
			else:
				print("Active windows does not match any defined programs")
			print("Sleeping...")
			time.sleep(self.refreshRate)

if __name__ == "__main__":
		m = MovieMode()
		m.start()
