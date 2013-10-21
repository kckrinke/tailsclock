#!/usr/bin/env python
"""
Tails Clock Applet

A simple GNOME panel applet (GNOME 2.x or GNOME 3 in fallback/classic mode)
that displays the date and time. The clock applet defaults to UTC, however,
users can configure the timezone in the applet's preferences. Changing the
timezone in the applet does not affect any actual part of the operating
system with the exception of storing the currently selected timezone in
~/.config/tails/timezone

Author: Kevin C. Krinke <kevin@krinke.ca>
License: GNU Public License 2.0 (or greater)

Project based on initial code that was generated using the following project:
 https://github.com/palfrey/panel-applet-generator
"""
import os, sys, re
from datetime import datetime, tzinfo, timedelta
import time
import locale
import pytz
import gettext
gettext.install('tailsclockapplet', unicode=1) #: system default

#: load up Gtk
try:
    from gi.repository import Gtk, GObject, Gdk
except: # Can't use ImportError, as gi.repository isn't quite that nice...
    import gtk as Gtk
    import gobject as GObject
    import gtk.gdk as Gdk

# Consolidate default values
DEFAULT_CFG_DATA = {'show_sec':False,'show_12hr':False,'show_tz':False,'tz':'UTC'}

class TailsClockPrefsDialog:
    """
    Simple preferences dialog for Tails Clock. Currently supports changing
    the timezone for the clock display. Changes propagate immediately.
    """
    applet = None
    dialog = None
    tz_tview = None
    tz_store = None
    show_12hr = None
    show_tz = None
    show_sec = None

    def __init__(self,applet):
        #: store the applet's reference for later
        self.applet = applet
        self.dialog = Gtk.Dialog(_("Tails Clock Preferences"),
                                 None, Gtk.DialogFlags.MODAL,
                                 (Gtk.STOCK_CLOSE,Gtk.ResponseType.OK)
                                 )
        #: construct the core dialog
        vbox = self.dialog.get_content_area()
        #: setup a notebook
        nbook = Gtk.Notebook()
        nbook.set_show_tabs(True)
        nbook.set_show_border(True)
        vbox.pack_start(nbook,True,True,8)
        #: General Settings
        tbl = Gtk.VBox()
        self.show_12hr = Gtk.CheckButton(_("12 Hour Clock?"))
        self.show_12hr.set_active(self.applet.show_12hr)
        self.show_12hr.connect('toggled',self.toggled_12hr)
        tbl.pack_start(self.show_12hr,True,True,8)
        self.show_sec = Gtk.CheckButton(_("Display Seconds?"))
        self.show_sec.set_active(self.applet.show_sec)
        self.show_sec.connect('toggled',self.toggled_sec)
        tbl.pack_start(self.show_sec,True,True,8)
        self.show_tz = Gtk.CheckButton(_("Display Timezone?"))
        self.show_tz.set_active(self.applet.show_tz)
        self.show_tz.connect('toggled',self.toggled_tz)
        tbl.pack_start(self.show_tz,True,True,8)
        nbook.append_page(tbl,Gtk.Label(_("General")))
        #: Time Zone Configuration
        tz_vbox = Gtk.VBox()
        nbook.append_page(tz_vbox,Gtk.Label(_("Timezone")))
        tz_label = Gtk.Label(_("Please select a timezone from the following list:"))
        tz_label.set_line_wrap(True)
        tz_label.set_width_chars(42)
        tz_vbox.pack_start(tz_label,False,False,8)
        self.tz_store = Gtk.ListStore(str)
        self.tz_tview = Gtk.TreeView(self.tz_store)
        self.tz_tview.set_headers_visible(False)
        tz_rndrr = Gtk.CellRendererText()
        tz_col = Gtk.TreeViewColumn(_("Timezones"), tz_rndrr, text = 0)
        self.tz_tview.append_column(tz_col)
        tz_scroll = Gtk.ScrolledWindow(hadjustment=None,vadjustment=None)
        tz_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        tz_scroll.add(self.tz_tview)
        tz_frame = Gtk.Frame()
        tz_frame.add(tz_scroll)
        #: Add timezones to the list and pre-select the current timezone
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
        tz_vbox.pack_start(tz_frame,True,True,8)
        select.connect("changed",self.on_timezone_selection_changed)
        select.set_mode(Gtk.SelectionMode.SINGLE)
        #: try to constrain the dialog's size
        nbook.show_all()
        self.dialog.set_size_request(280,280)
        self.dialog.set_resizable(False)
        pass

    def update_general(self):
        data = DEFAULT_CFG_DATA.copy()
        data['show_12hr'] = self.show_12hr.get_active()
        data['show_sec'] = self.show_sec.get_active()
        data['show_tz'] = self.show_tz.get_active()
        self.applet.update_cfg(data)
        pass

    def toggled_12hr(self,widget):
        self.update_general()
        pass
    def toggled_sec(self,widget):
        self.update_general()
        pass
    def toggled_tz(self,widget):
        self.update_general()
        pass

    def on_timezone_selection_changed(self,selection):
        """
        Whenever the user selects a timezone, update the clock display
        immediately.
        """
        model, treeiter = selection.get_selected()
        if treeiter != None:
            new_tz = model[treeiter][0]
            self.applet.update_cfg({'tz':new_tz})
        pass

    def run(self):
        """
        Helper method to actually display the dialog (and all of the
        widgets contained therein.
        """
        self.dialog.show_all()
        rv = self.dialog.run()
        # retrieve pref values
        self.dialog.destroy()
        return


class TailsClock:
    """
    Actual class used to manage the applet and display the time.
    """
    main_label = None
    main_evbox = None
    main_menu = None

    panel_applet = None
    panel_iid = None
    panel_data = None

    glib_timer = None

    tz_info = None
    tz_name = None
    cfg_path = None
    cfg_tz_path = None

    show_tz = DEFAULT_CFG_DATA['show_tz']
    show_sec = DEFAULT_CFG_DATA['show_sec']
    show_12hr = DEFAULT_CFG_DATA['show_12hr']

    def __init__(self,applet,iid,data):
        """
        Simple initialization of the class instance.
        """
        # live or debug?
        if applet.__class__ is not Gtk.Window:
            applet.set_background_widget(applet)
        else:
            # debug; load translations from "here"
            gettext.install('tailsclockapplet', './locale', unicode=1)
        self.cfg_path = os.environ['HOME']+"/.config/tailsclock/settings"
        self.cfg_tz_path = os.environ['HOME']+"/.config/tailsclock/timezone"
        self.panel_applet = applet
        self.panel_iid = iid
        self.panel_data = data
        self.create_menu()
        pass

    def create_menu(self):
        """
        Generate a left-click context-menu
        """
        self.main_menu = Gtk.Menu()
        pref_item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_PREFERENCES,None)
        pref_item.connect("activate",self.display_prefs,self)
        pref_item.show()
        self.main_menu.append(pref_item)
        self.main_menu.show_all()
        return True

    def refresh_cfg(self):
        """
        Read the contents of the configuration file and update the clock
        accordingly. Tries to handle failures gracefully.
        """
        if os.path.exists(self.cfg_tz_path):
            contents = self._read_file(self.cfg_tz_path)
            try:
                self.tz_info = pytz.timezone(contents.strip())
                self.tz_name = contents
            except Exception, e:
                sys.stderr.write("TailsClock Invalid Timezone: "+str(e)+"\n")
                self.tz_info = None
        if self.tz_info is None:
            self.tz_name = "UTC"
            self.tz_info = pytz.utc
        if os.path.exists(self.cfg_path):
            data = self._read_yaml(self.cfg_path)
            if data.has_key('show_tz'):
                self.show_tz = bool(data['show_tz'])
            if data.has_key('show_sec'):
                self.show_sec = bool(data['show_sec'])
            if data.has_key('show_12hr'):
                self.show_12hr = bool(data['show_12hr'])
        return

    def _write_file(self,path,contents):
        try:
            fh = open(path,'w')
            fh.write(contents)
            fh.close()
        except Exception, e:
            sys.stderr.write("TailsClock[_write_file]: " + str(e) + "\n")
            return False
        return True

    def _write_yaml(self,path,data):
        current = self._read_yaml(path)
        yaml = ""
        for k in current.keys():
            if data.has_key(k):
                yaml += k+":"+str(data[k])+"\n"
            else:
                yaml += k+":"+str(current[k])+"\n"
        return self._write_file(path,yaml)

    def _read_file(self,path):
        val = ""
        try:
            fh = open(path,'r')
            val = fh.read()
            fh.close()
            val = val.strip()
        except Exception, e:
            sys.stderr.write("TailsClock[_read_file]: " + str(e) + "\n")
            return None
        return val

    def _read_yaml(self,path):
        val = DEFAULT_CFG_DATA.copy()
        raw = None
        try:
            fh = open(path,'r')
            raw = fh.read()
            fh.close()
        except Exception, e:
            sys.stderr.write("TailsClock[_read_yaml]: " + str(e) + "\n")
            return val
        lines = raw.splitlines()
        for line in lines:
            line = line.strip()
            (k,v) = re.split("\s*:\s*",line)
            if v == 'True': v = True
            if v == 'False': v = False
            val[k] = v
        return val

    def update_cfg(self,data):
        """
        Overwrites the timezone configuration file with the given data.
        """
        if data.has_key('tz'):
            self._write_file(self.cfg_tz_path,data['tz'])
            del data['tz']
        if len(data) > 0:
            self._write_yaml(self.cfg_path,data)
        self.refresh_cfg()
        self.update_time()
        return

    def launch(self):
        """
        Construct the user-interface, stylize the widgets, connect the timers
        and so on. Basically; launch the applet.
        """
        # actually populate UI
        self.main_label = Gtk.Label("...")
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
            font-weight: bold;
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
        self.refresh_cfg()
        self.update_time()
        return self

    def update_glib_timer(self):
        if self.glib_timer != None:
            GObject.source_remove(self.glib_timer)
            self.glib_timer = None
        if self.show_sec:
            self.glib_timer = GObject.timeout_add(1000,self.update_time)
        else:
            now = datetime.now()
            min = datetime(now.year,now.month,now.day,now.hour,now.minute+1)
            delta = (min-now).seconds * 1000 + 999
            self.glib_timer = GObject.timeout_add(delta,self.update_time)
        return False

    def update_time(self):
        """
        Fired once-per second to update the time.
        """
        # get the date/time and apply tz_info to it
        utc_dt = datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        dt = utc_dt.astimezone(self.tz_info)
        # format the date/time stamp
        dt_format = locale.nl_langinfo(locale.D_T_FMT)
        if '%r' in dt_format:
            if self.show_sec:
                if self.show_12hr:
                    dt_format = re.sub("%r","%I:%M:%S %p",dt_format)
                else:
                    dt_format = re.sub("%r","%H:%M:%S",dt_format)
            else:
                if self.show_12hr:
                    dt_format = re.sub("%r","%I:%M %p",dt_format)
                else:
                    dt_format = re.sub("%r","%H:%M",dt_format)
                pass
        else:
            sys.stderr.write("TailsClock: there's no %%r?!")
        if '%Z' in dt_format and not self.show_tz:
            dt_format = re.sub("\s*%Z","",dt_format)
        stamp = dt.strftime(dt_format)
        # actually update the label
        self.main_label.set_text(stamp)
        return self.update_glib_timer()

    def display_prefs(self,*argv):
        """
        Display the Tails Clock Preferences dialog.
        """
        TailsClockPrefsDialog(self).run()
        pass

    def display_menu(self,widget,event):
        """
        Trigger the context-menu to popup.
        """
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 3 and (event.state & Gdk.ModifierType.MOD1_MASK) == False:
            # popup(self, parent_menu_shell, parent_menu_item, func, data, button, activate_time)
            self.main_menu.popup(None,None,None,None,event.button,event.time)
            return True
        return False


    
tc_inst = None
def applet_factory(applet, iid, data = None):
    """
    Construct the clock instance and launch it.
    """
    tc_inst = TailsClock(applet,iid,data).launch()
    return True
