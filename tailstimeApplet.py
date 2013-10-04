#!/usr/bin/env python

from time import time

try:
    from gi.repository import Gtk, GObject
except: # Can't use ImportError, as gi.repository isn't quite that nice...
    import gtk as Gtk
    import gobject as GObject

class tailstime:
    main_label = None

    panel_applet = None
    panel_iid = None
    panel_data = None

    def __init__(self,applet,iid,data):
        # not sure why, but let's save this
        self.panel_applet = applet
        self.panel_iid = iid
        self.panel_data = data
        pass

    def launch(self):
        # actually populate UI
        self.main_label = Gtk.Label("It works!")
        self.panel_applet.add(self.main_label)
        self.panel_applet.show_all()
        self.update_time()
        GObject.timeout_add(1000,self.update_time)
        return self

    def update_time(self):
        stamp = "T %d" % time()
        self.main_label.set_text(stamp)
        self.panel_applet
        return True
    
tt_inst = None
def applet_factory(applet, iid, data = None):
    tt_inst = tailstime(applet,iid,data).launch()
    return True
