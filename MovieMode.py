#!/usr/bin/python
import subprocess, dbus,os, time,re
class MovieMode:
	def __init__(self):
		self.sleepIsPrevented = False
		self.redshiftIsKilled = False
		self.matches = ['pipelight-silverlight', 'vlc']
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
				if "redshift" in line:
					print("matched redshift on line " + line)
					matches = re.findall(r"\d{2,}",line)
					if matches:
						# kill the pid of redshift
						print("killing redshift on pid " + matches[0])
						subprocess.Popen('kill ' + matches[0], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
						self.redshiftIsKilled = True
						break

	def start(self):
		disabled = False
		while(True):
			isRunning = self.processesRunning()
			if isRunning and not disabled or not isRunning and disabled:
				self.toggleScreenSaver()
				self.toggleRedshift()
				disabled = not disabled
			print("Sleeping...")
			time.sleep(30)

if __name__ == "__main__":
		m = MovieMode()
		m.start()
