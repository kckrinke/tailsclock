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
    tailsclock = None
    def __init__(self, applet):
        self.tailsclock = applet
        Gtk.Dialog.__init__(self, "TailsClock Preferences", None, 0,
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
    main_evbox = None
    main_menu = None

    panel_applet = None
    panel_iid = None
    panel_data = None

    tz_info = None

    def __init__(self,applet,iid,data):
        # transparent background?
        #applet.set_background_widget(applet)
        # not sure why, but let's save this
        self.panel_applet = applet
        self.panel_iid = iid
        self.panel_data = data
        self.create_menu()
        pass

    def create_menu(self):
        self.main_menu = Gtk.Menu()
        pref_item = Gtk.MenuItem("Preferences")
        pref_item.connect("activate",self.display_prefs,self)
        pref_item.show()
        self.main_menu.append(pref_item)
        self.main_menu.show_all()
        return True

    def refresh_cfg(self):
        cfg_path = os.environ['HOME']+"/.config/tails/timezone"
        if os.path.exists(cfg_path):
            fh = open(cfg_path,'r')
            try:
                contents = fh.read()
                contents = re.sub("\s","",contents)
                self.tz_info = pytz.timezone(contents)
            except Exception, e:
                sys.stderr.write("TailsClock Invalid Timezone: "+str(e)+"\n")
                os.remove(cfg_path)
                self.tz_info = None
            fh.close()
        if self.tz_info is None:
            self.tz_info = pytz.utc
        return

    def launch(self):
        # actually populate UI
        self.refresh_cfg()
        self.main_label = Gtk.Label("Initializing...")
        self.main_evbox = Gtk.EventBox()
        self.main_evbox.modify_bg(Gtk.StateFlags.NORMAL,Gdk.color_parse("black"))
        self.main_evbox.add(self.main_label)
        self.main_evbox.connect("button-release-event",self.display_menu)
        self.panel_applet.add(self.main_evbox)
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

    def display_prefs(self,widget,event):
        tcp = TailsClockPreferences(self)
        tcp.run()
        tcp.destroy()
        pass

    def display_menu(self,widget,event):
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 1:
            # popup(self, parent_menu_shell, parent_menu_item, func, data, button, activate_time)
            self.main_menu.popup(None,None,None,None,event.button,event.time)
            return True
        return False


    
tc_inst = None
def applet_factory(applet, iid, data = None):
    tc_inst = TailsClock(applet,iid,data).launch()
    return True
