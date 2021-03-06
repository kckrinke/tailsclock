#!/usr/bin/env python

import sys
import gtk
import pygtk
pygtk.require('2.0')
import gnomeapplet
from TailsClockApplet import applet_factory

if __name__ == '__main__':	 # testing for execution

	if len(sys.argv) > 1 and sys.argv[1] == '-d': # debugging
		mainWindow = gtk.Window()
		mainWindow.set_title('Tails Clock Window')
		mainWindow.connect('destroy', gtk.main_quit)
		applet = gnomeapplet.Applet()
		applet_factory(applet, None, None, True)
		applet.reparent(mainWindow)
		mainWindow.show_all()
		gtk.main()
		sys.exit()
	else:
		gnomeapplet.bonobo_factory('OAFIID:TailsClock_Factory', 
				gnomeapplet.Applet.__gtype__, 
				'TailsClock',
				'0.1', 
				applet_factory)
