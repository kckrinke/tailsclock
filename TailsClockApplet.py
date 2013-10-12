#!/usr/bin/env python
import os, sys, re
from datetime import datetime, tzinfo, timedelta
import time
import locale
import pytz

try:
    from gi.repository import Gtk, GObject, Gdk
except: # Can't use ImportError, as gi.repository isn't quite that nice...
    import gtk as Gtk
    import gobject as GObject
    import gtk.gdk as Gdk


class TailsClockPreferences(Gtk.Dialog):
    parent = None
    def __init__(self, tailsclock):
        self.parent = tailsclock
        Gtk.Dialog.__init__(self, "My Dialog", self.parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(150, 100)
        label = Gtk.Label("This is a dialog to display additional information")
        # need to populate options from pytz.common_timezones
        box = self.get_content_area()
        box.add(label)
        self.show_all()
        pass


class TailsClock:
    main_label = None

    panel_applet = None
    panel_iid = None
    panel_data = None

    tz_info = None

    def __init__(self,applet,iid,data):
        # not sure why, but let's save this
        self.panel_applet = applet
        self.panel_iid = iid
        self.panel_data = data
        pass

    def refresh_cfg(self):
        #self.tz_info = pytz.timezone('Canada/Eastern')
        #self.tz_info = pytz.timezone('Canada/Pacific')
        #self.tz_info = pytz.timezone('Canada/Central')
        cfg_path = os.environ['HOME']+"/.config/tails/timezone"
        print cfg_path
        if os.path.exists(cfg_path):
            print "exists"
            fh = open(cfg_path,'r')
            try:
                contents = fh.read()
                contents = re.sub("\s","",contents)
                self.tz_info = pytz.timezone(contents)
            except Exception( e ):
                print e
                self.tz_info = None
            fh.close()
        else:
            print "not exist"
        if self.tz_info is None:
            self.tz_info = pytz.utc
        pass

    def launch(self):
        # actually populate UI
        self.refresh_cfg()
        self.main_label = Gtk.Label("Initializing...")
        self.panel_applet.add(self.main_label)
        self.panel_applet.show_all()
        self.update_time()
        GObject.timeout_add(1000,self.update_time)
        return self

    def update_time(self):
        utc_dt = datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        dt = utc_dt.astimezone(self.tz_info)
        dt_format = locale.nl_langinfo(locale.D_T_FMT)
        stamp = dt.strftime(dt_format)
        self.main_label.set_text(stamp)
        return True
    
tc_inst = None
def applet_factory(applet, iid, data = None):
    tc_inst = TailsClock(applet,iid,data).launch()
    return True
