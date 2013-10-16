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

class TailsClockPrefsDialog:
    applet = None
    dialog = None
    tz_tview = None
    tz_store = None

    def __init__(self,applet):
        self.applet = applet
        self.dialog = Gtk.Dialog("Tails Clock Preferences",None,Gtk.DialogFlags.MODAL,
                                 ("Close",Gtk.ResponseType.OK)
                                 )
        vbox = self.dialog.get_content_area()
        #: Time Zone Configuration
        tz_label = Gtk.Label("Please select a timezone from the following list:")
        tz_label.set_line_wrap(True)
        vbox.pack_start(tz_label,False,False,1)
        self.tz_store = Gtk.ListStore(str)
        self.tz_tview = Gtk.TreeView(self.tz_store)
        self.tz_tview.set_headers_visible(False)
        tz_rndrr = Gtk.CellRendererText()
        tz_col = Gtk.TreeViewColumn("Timezones", tz_rndrr, text = 0)
        self.tz_tview.append_column(tz_col)
        tz_scroll = Gtk.ScrolledWindow(hadjustment=None,vadjustment=None)
        tz_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        tz_scroll.add(self.tz_tview)
        vbox.pack_start(tz_scroll,True,True,1)
        select = self.tz_tview.get_selection()
        for tz in pytz.common_timezones:
            tmpiter = self.tz_store.append([tz])
            if self.applet.tz_name != None:
                if self.applet.tz_name == tz:
                    select.select_iter(tmpiter)
                    tmppath = self.tz_store.get_path(tmpiter)
                    self.tz_tview.scroll_to_cell(tmppath,None,False,0,0)
                    pass
                pass
            pass
        select.connect("changed",self.on_timezone_selection_changed)
        select.set_mode(Gtk.SelectionMode.SINGLE)
        self.dialog.set_size_request(250,250)
        self.dialog.set_resizable(False)
        pass

    def on_timezone_selection_changed(self,selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            new_tz = model[treeiter][0]
            self.applet.update_cfg({'tz':new_tz})
        pass

    def run(self):
        self.dialog.show_all()
        rv = self.dialog.run()
        # retrieve pref values
        self.dialog.destroy()
        return


class TailsClock:
    main_label = None
    main_evbox = None
    main_menu = None

    panel_applet = None
    panel_iid = None
    panel_data = None

    tz_info = None
    tz_name = None
    cfg_path = None

    def __init__(self,applet,iid,data):
        self.cfg_path = os.environ['HOME']+"/.config/tails/timezone"
        # transparent background?
        if applet.__class__ is not Gtk.Window:
            applet.set_background_widget(applet)
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
        if os.path.exists(self.cfg_path):
            fh = open(self.cfg_path,'r')
            try:
                contents = fh.read()
                contents = re.sub("\r??\n","",contents)
                self.tz_info = pytz.timezone(contents.strip())
                self.tz_name = contents
            except Exception, e:
                sys.stderr.write("TailsClock Invalid Timezone: "+str(e)+"\n")
                os.remove(self.cfg_path)
                self.tz_info = None
                self.tz_name = contents
            fh.close()
        if self.tz_info is None:
            self.tz_info = pytz.utc
        return

    def update_cfg(self,data):
        if data.has_key('tz'):
            fh = open(self.cfg_path,'w')
            try:
                fh.write(data['tz'])
                pass
            except Exception, e:
                os.remove(self.cfg_path)
            fh.close()
        self.refresh_cfg()
        return

    def launch(self):
        # actually populate UI
        self.refresh_cfg()
        self.main_label = Gtk.Label("Initializing...")
        self.main_label.set_name("TailsClockAppletLabel")
        self.main_evbox = Gtk.EventBox()
        self.main_evbox.set_name("TailsClockAppletEvBox")
        self.main_evbox.add(self.main_label)
        self.main_evbox.connect("button-release-event",self.display_menu)
        # transparent background style
        style_provider = Gtk.CssProvider()
        css = """
        #TailsClockAppletLabel,#TailsClockAppletEvBox {
            background-color: rgba(0,0,0,0);
        }
        """
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        # add/show all
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

    def display_prefs(self,*argv):
        TailsClockPrefsDialog(self).run()
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
