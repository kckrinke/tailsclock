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

IS_DEBUG=False
def debug_log(message):
    global IS_DEBUG
    if not IS_DEBUG:
        return False
    sys.stderr.write("TailsClock: "+message+"\n")
    try:
        fh = open("/tmp/tailsclockapplet.log","a")
        fh.write(message+"\n")
        fh.close()
    except Exception, e:
        sys.stderr.write("TailsClock: Exception caught: ("+str(e)+")\n")
    return True

#: load up Gtk
IS_GTK3=True
try:
    from gi.repository import Gtk, GObject, Gdk
except: # Can't use ImportError, as gi.repository isn't quite that nice...
    IS_GTK3=False
    import gtk as Gtk
    import gobject as GObject
    import gtk.gdk as Gdk

# Consolidate default values
DEFAULT_CFG_DATA = {
    'show_sec':False,
    'show_12hr':True,
    'show_tz':False,
    'show_yr':False,
    'show_dt':True,
    }

class TailsClockConfig:
    cfg_base = None
    cfg_rc_path = None
    cfg_tz_path = None
    
    show_tz = DEFAULT_CFG_DATA['show_tz']
    show_sec = DEFAULT_CFG_DATA['show_sec']
    show_12hr = DEFAULT_CFG_DATA['show_12hr']
    show_yr = DEFAULT_CFG_DATA['show_yr']
    show_dt = DEFAULT_CFG_DATA['show_dt']
    show_time = True #< don't actually store this setting

    tz_info = pytz.timezone('UTC')
    tz_name = 'UTC'

    def __init__(self):
        self.cfg_base = os.environ['HOME']+"/.config/tailsclock"
        if not os.path.exists(self.cfg_base):
            try:
                os.makedirs(self.cfg_base)
            except Exception, e:
                debug_log("Failed to make tailsclock config path: "+str(e))
        self.cfg_rc_path = self.cfg_base + "/settings"
        self.cfg_tz_path = self.cfg_base + "/timezone"
        self.load()
        pass

    def load(self):
        if os.path.exists(self.cfg_tz_path):
            contents = self._read_file(self.cfg_tz_path)
            try:
                self.tz_info = pytz.timezone(contents.strip())
                self.tz_name = contents
            except Exception, e:
                debug_log("Invalid Timezone: "+str(e)+"\n")
                self.tz_info = None
        if self.tz_info is None:
            self.tz_name = "UTC"
            self.tz_info = pytz.utc
        if os.path.exists(self.cfg_rc_path):
            data = self._read_yaml(self.cfg_rc_path)
            if data.has_key('show_tz'):   self.show_tz   = bool(data['show_tz'])
            if data.has_key('show_sec'):  self.show_sec  = bool(data['show_sec'])
            if data.has_key('show_12hr'): self.show_12hr = bool(data['show_12hr'])
            if data.has_key('show_yr'):   self.show_yr   = bool(data['show_yr'])
            if data.has_key('show_dt'):   self.show_dt   = bool(data['show_dt'])
        return True

    def save(self,data=None):
        if data is None:
            data = {
                'show_tz': self.show_tz,
                'show_sec': self.show_sec,
                'show_12hr': self.show_12hr,
                'show_yr': self.show_yr,
                'show_dt': self.show_dt,
                }
        if data.has_key('tz'):
            self._write_file(self.cfg_tz_path,data['tz'])
            del data['tz']
        if len(data) > 0:
            self._write_yaml(self.cfg_rc_path,data)
        return True

    def copy(self):
        clone = TailsClockConfig()
        clone.tz_info = self.tz_info
        clone.tz_name = self.tz_name
        clone.show_tz = self.show_tz
        clone.show_sec = self.show_sec
        clone.show_12hr = self.show_12hr
        clone.show_yr = self.show_yr
        clone.show_dt = self.show_dt
        return clone

    def _write_file(self,path,contents):
        try:
            fh = open(path,'w')
            fh.write(contents)
            fh.close()
        except Exception, e:
            debug_log("_write_file: " + str(e) + "\n")
            return False
        return True

    def _write_yaml(self,path,data):
        current = self._read_yaml(path)
        yaml = ""
        for k in current.keys():
            if k is 'tz':
                next
            if data.has_key(k):
                yaml += k+":"+str(data[k])+"\n"
            else:
                yaml += k+":"+str(current[k])+"\n"
        return self._write_file(path,yaml)

    def _read_file(self,path):
        if not os.path.exists(path):
            return None
        val = ""
        try:
            fh = open(path,'r')
            val = fh.read()
            fh.close()
            val = val.strip()
        except Exception, e:
            debug_log("_read_file: " + str(e) + "\n")
            return None
        return val

    def _read_yaml(self,path):
        val = DEFAULT_CFG_DATA.copy()
        if not os.path.exists(path):
            return val
        raw = None
        try:
            fh = open(path,'r')
            raw = fh.read()
            fh.close()
        except Exception, e:
            debug_log("_read_yaml: " + str(e) + "\n")
            return val
        lines = raw.splitlines()
        for line in lines:
            line = line.strip()
            (k,v) = re.split("\s*:\s*",line)
            if v == 'True': v = True
            else: v = False
            val[k] = v
        return val




class TailsClockPrefsDialog(Gtk.Dialog):
    """
    Simple preferences dialog for Tails Clock. Currently supports changing
    the timezone for the clock display. Changes propagate immediately.
    """
    applet = None
    dialog = None
    tz_tview = None
    tz_store = None
    # note: the following vars are widgets, not actual config
    show_12hr = None
    show_tz = None
    show_sec = None
    show_yr = None
    show_dt = None

    def _add_pref_checkbox(self,box,title,state,func):
        bttn = Gtk.CheckButton(title)
        bttn.set_active(state)
        bttn.connect('toggled',func)
        hbox = Gtk.HBox()
        hbox.pack_start(bttn,True,True,8)
        box.pack_start(hbox,True,True,8)
        return bttn

    def __init__(self,applet):
        #: store the applet's reference for later
        self.panel_applet = applet
        #: initialize self
        if IS_GTK3:
            flags = Gtk.DialogFlags.MODAL
            buttons = (Gtk.STOCK_ABOUT,Gtk.ResponseType.ACCEPT,Gtk.STOCK_CLOSE,Gtk.ResponseType.OK)
        else:
            flags = Gtk.DIALOG_MODAL | Gtk.DIALOG_NO_SEPARATOR
            buttons = (Gtk.STOCK_ABOUT,Gtk.RESPONSE_ACCEPT,Gtk.STOCK_CLOSE,Gtk.RESPONSE_OK)
        Gtk.Dialog.__init__(self,_("Tails Clock Preferences"),None,flags,buttons)
        self.set_modal(True)
        self.set_size_request(280,280)
        self.set_resizable(False)
        #: construct the core dialog
        #: setup a notebook
        nbook = Gtk.Notebook()
        nbook.set_show_tabs(True)
        nbook.set_show_border(True)
        content_hbox = Gtk.HBox()
        content_hbox.pack_start(nbook,True,True,6)
        self.vbox.pack_start(content_hbox,True,True,8)
        #: General Settings
        tbl = Gtk.VBox()
        self.show_12hr = self._add_pref_checkbox(tbl,_("12 Hour Clock?"),self.panel_applet.config.show_12hr,self.toggled_12hr)
        self.show_sec = self._add_pref_checkbox(tbl,_("Display seconds?"),self.panel_applet.config.show_sec,self.toggled_sec)
        self.show_tz = self._add_pref_checkbox(tbl,_("Display Timezone?"),self.panel_applet.config.show_tz,self.toggled_tz)
        self.show_yr = self._add_pref_checkbox(tbl,_("Display Year?"),self.panel_applet.config.show_yr,self.toggled_yr)
        self.show_dt = self._add_pref_checkbox(tbl,_("Display Date?"),self.panel_applet.config.show_dt,self.toggled_dt)
        nbook.append_page(tbl,Gtk.Label(_("General")))
        #: Time Zone Configuration
        tz_vbox = Gtk.VBox()
        nbook.append_page(tz_vbox,Gtk.Label(_("Timezone")))
        self.tz_store = Gtk.ListStore(str)
        self.tz_tview = Gtk.TreeView(self.tz_store)
        self.tz_tview.set_headers_visible(False)
        tz_rndrr = Gtk.CellRendererText()
        tz_col = Gtk.TreeViewColumn(_("Timezones"), tz_rndrr, text = 0)
        self.tz_tview.append_column(tz_col)
        tz_scroll = Gtk.ScrolledWindow(hadjustment=None,vadjustment=None)
        if IS_GTK3:
            tz_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        else: # NOT_GTK3
            tz_scroll.set_policy(Gtk.POLICY_AUTOMATIC,Gtk.POLICY_AUTOMATIC)
        tz_scroll.add(self.tz_tview)
        tz_frame = Gtk.Frame()
        tz_frame.add(tz_scroll)
        #: Add timezones to the list and pre-select the current timezone
        select = self.tz_tview.get_selection()
        for tz in pytz.common_timezones:
            tmpiter = self.tz_store.append([tz])
            if self.panel_applet.config.tz_name != None:
                if self.panel_applet.config.tz_name == tz:
                    select.select_iter(tmpiter)
                    tmppath = self.tz_store.get_path(tmpiter)
                    self.tz_tview.scroll_to_cell(tmppath,None,False,0,0)
                    pass
                pass
            pass
        tz_vbox.pack_start(tz_frame,True,True,0)
        select.connect("changed",self.on_timezone_selection_changed)
        if IS_GTK3:
            select.set_mode(Gtk.SelectionMode.SINGLE)
        else: # NOT_GTK3
            select.set_mode(Gtk.SELECTION_SINGLE)
        #: try to constrain the dialog's size
        nbook.show_all()
        pass

    def close(self,widget,event):
        self.destroy()
        return True

    def update_general(self):
        data = DEFAULT_CFG_DATA.copy()
        data['show_12hr'] = self.show_12hr.get_active()
        data['show_sec'] = self.show_sec.get_active()
        data['show_tz'] = self.show_tz.get_active()
        data['show_yr'] = self.show_yr.get_active()
        data['show_dt'] = self.show_dt.get_active()
        self.panel_applet.update_cfg(data)
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
    def toggled_yr(self,widget):
        self.update_general()
        pass
    def toggled_dt(self,widget):
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
            self.panel_applet.update_cfg({'tz':new_tz})
        pass

    def run(self):
        """
        Helper method to actually display the dialog (and all of the
        widgets contained therein.
        """
        self.show_all()
        if IS_GTK3:
            rv = super(Gtk.Dialog,self).run()
            self.destroy()
            if rv == Gtk.ResponseType.ACCEPT:
                TailsClockAboutDialog().run()
        else:
            rv = Gtk.Dialog.run(self)
            self.destroy()
            if rv == Gtk.RESPONSE_ACCEPT:
                TailsClockAboutDialog().run()
        return


class TailsClockAboutDialog(Gtk.AboutDialog):
    """
    Basic About Dialog
    """

    def __init__(self):
        Gtk.AboutDialog.__init__(self)
        self.set_size_request(300,150)
        self.set_modal(True)
        self.set_name("Tails Clock")
        self.set_program_name("Tails Clock")
        self.set_version("0.3")
        self.set_copyright("GPL2")
        self.set_comments("A simple GNOME panel applet clock.")
        pass

    def run(self):
        """
        Helper method to actually display the dialog (and all of the
        widgets contained therein.
        """
        self.show_all()
        rv = super(Gtk.AboutDialog,self).run()
        self.destroy()
        return

class TailsClockCalendarWindow(Gtk.Window):
    """
    Simple Calendar, mimics basic feature of actual GNOME Panel Clock.
    Based on a stackoverflow answer:
    http://stackoverflow.com/questions/11132929/showing-a-gtk-calendar-in-a-menu/11261043#11261043
    """
    toggle_button = None
    def __init__(self,button):
        self.toggle_button = button
        if IS_GTK3:
            #cal_window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
            super(TailsClockCalendarWindow,self).__init__(Gtk.WindowType.TOPLEVEL)
            self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        else:
            #cal_window = Gtk.Window(Gtk.WINDOW_TOPLEVEL)
            super(TailsClockCalendarWindow,self).__init__(Gtk.WINDOW_TOPLEVEL)
            #cal_window.set_type_hint(Gtk.gdk.WINDOW_TYPE_HINT_DOCK)
            self.set_type_hint(Gtk.gdk.WINDOW_TYPE_HINT_DOCK)
        self.set_decorated(False)
        self.set_resizable(False)
        self.stick()
        cal_vbox = Gtk.VBox(False, 10)
        self.add(cal_vbox)
        cal_vbox.pack_start(Gtk.Calendar(), True, False, 0)
        #self.connect("configure-event", self.on_window_config, self.toggle_button)
        pass

    def show_calendar(self):
        rect = self.toggle_button.get_allocation()
        main_window = self.toggle_button.get_toplevel()
        [win_x, win_y] = main_window.get_window().get_root_coords(0,0)
        cal_x = win_x + rect.x
        cal_y = win_y + rect.y + rect.height
        [x, y] = self.apply_screen_coord_correction(cal_x, cal_y, self, self.toggle_button)
        debug_log("on_toggle: X:%d,Y:%d,WX:%d,WY:%d,CX:%d,CY:%d" % (x,y,win_x,win_y,cal_x,cal_y))
        self.move(x, y)
        self.show_all()
        return True

    def hide_calendar(self):
        self.hide()
        return True

    def toggle(self):
        if self.toggle_button.get_active():
            self.show_calendar()
        else:
            self.hide_calendar()
        return

    # This function "tries" to correct calendar window position so that it is not obscured when
    # a portion of main window is off-screen.
    # Known bug: If the main window is partially off-screen before Calendar window
    # has been realized then get_allocation() will return rect of 1x1 in which case
    # the calculations will fail & correction will not be applied
    def apply_screen_coord_correction(self, x, y, widget, relative_widget):
        corrected_y = y
        corrected_x = x
        rect = widget.get_allocation()
        if IS_GTK3:
            screen_w = Gdk.Screen.get_default().get_width()
            screen_h = Gdk.Screen.get_default().get_height()
        else:
            screen_w = Gdk.screen_width()
            screen_h = Gdk.screen_height()
        delta_x = screen_w - (x + rect.width)
        delta_y = screen_h - (y + rect.height)
        if delta_x < 0:
            corrected_x += delta_x
        if corrected_x < 0:
            corrected_x = 0
        if delta_y < 0:
            corrected_y = y - rect.height - relative_widget.get_allocation().height
        if corrected_y < 0:
            corrected_y = 0
        return [corrected_x, corrected_y]


class TailsClock:
    """
    Actual class used to manage the applet and display the time.
    """
    main_bttn = None
    main_menu = None
    main_drop = None #Currently just a Calendar

    panel_applet = None
    panel_iid = None
    panel_data = None

    glib_timer = None

    cfg_base = None
    cfg_rc_path = None
    cfg_tz_path = None

    config = None

    def __init__(self,applet,iid,data):
        """
        Simple initialization of the class instance.
        """
        if IS_GTK3:
            debug_log("IS_GTK3")
        else:
            debug_log("NOT_GTK3")
        # live or debug?
        if applet.__class__ is not Gtk.Window:
            applet.set_background_widget(applet)
        else:
            # debug; load translations from "here"
            gettext.install('tailsclockapplet', './locale', unicode=1)
        self.config = TailsClockConfig()
        self.panel_applet = applet
        self.panel_iid = iid
        self.panel_data = data
        if IS_GTK3:
            self.create_menu3()
        else: # NOT_GTK3
            self.create_menu2()
        pass

    def _dt_format(self,cfg=None):
        """
        Not sure how reliable this method of formatting the dt string is.
        Different locales may impact formatting items. Need unit-tests heh
        """
        if cfg is None:
            cfg = self.config
        dt_format = ""
        if cfg.show_time:
            if cfg.show_dt:
                dt_format = locale.nl_langinfo(locale.D_T_FMT)
            else: # NOT show_dt
                dt_format = locale.nl_langinfo(locale.T_FMT)
                debug_log("dt_format:in1: '"+dt_format+"'")
            if '%r' in dt_format:
                if cfg.show_sec:
                    if cfg.show_12hr:
                        dt_format = re.sub("%r","%I:%M:%S %p",dt_format)
                    else:
                        dt_format = re.sub("%r","%H:%M:%S",dt_format)
                else:
                    if cfg.show_12hr:
                        dt_format = re.sub("%r","%I:%M %p",dt_format)
                    else:
                        dt_format = re.sub("%r","%H:%M",dt_format)
            if cfg.show_tz:
                if '%Z' not in dt_format:
                    dt_format = dt_format + " %Z"
            else:
                if '%Z' in dt_format:
                    dt_format = re.sub("\s*%Z","",dt_format)
        else: # NOT show_time
            dt_format = locale.nl_langinfo(locale.D_T_FMT)
            debug_log("dt_format:in2: '"+dt_format+"'")
            if '%r' in dt_format:
                dt_format = re.sub("\s??%r","",dt_format)
            if '%Z' in dt_format:
                dt_format = re.sub("\s??%Z","",dt_format)
        if ' %Y' in dt_format:
            if cfg.show_yr and not self.config.show_dt:
                dt_format = "%Y, " + dt_format
            elif cfg.show_yr:
                if cfg.show_time:
                    dt_format = re.sub(" %Y ",", %Y, ",dt_format)
                else:
                    dt_format = re.sub(" %Y",", %Y",dt_format)
            else:
                dt_format = re.sub(" %Y","",dt_format)
        if cfg.show_time and cfg.show_dt and not cfg.show_yr:
            dt_format = re.sub("%b %","%b, %",dt_format)
        debug_log("dt_format:out: '"+dt_format+"'")
        return dt_format

    def _add_menu3_item(self,title,stock_id,func,menu):
        if title is not None:
            item = Gtk.ImageMenuItem.new_with_label(title)
            item.set_image(Gtk.Image.new_from_stock(stock_id,Gtk.IconSize.MENU))
        else:
            item = Gtk.ImageMenuItem.new_from_stock(stock_id,None)
        item.connect("activate",func,self)
        menu.append(item)
        return

    def create_menu3(self):
        """
        Generate a left-click context-menu
        """
        debug_log("create_menu3")
        self.main_menu = Gtk.Menu()
        self._add_menu3_item(_("Copy Date"),Gtk.STOCK_COPY,self.copy_date,self.main_menu)
        self._add_menu3_item(_("Copy Time"),Gtk.STOCK_COPY,self.copy_time,self.main_menu)
        self._add_menu3_item(None,Gtk.STOCK_PREFERENCES,self.display_prefs,self.main_menu)
        self._add_menu3_item(None,Gtk.STOCK_ABOUT,self.display_about,self.main_menu)
        self.main_menu.show_all()
        return True

    def create_menu2(self):
        """
        Setup Gtk2 panel applet context-menu
        """
        debug_log("create_menu2")
        xml = '''
        <popup name="button3">
        <menuitem name="ItemCopy"
            verb="CopyDate"
            label="Copy Date"
            pixtype="stock"
            pixname="gtk-copy" />
        <menuitem name="ItemCopy"
            verb="CopyTime"
            label="Copy Time"
            pixtype="stock"
            pixname="gtk-copy" />
        <separator/>
        <menuitem name="ItemPreferences"
            verb="Preferences"
            label="_Preferences"
            pixtype="stock"
            pixname="gtk-preferences" />
        <menuitem name="ItemAbout"
            verb="About"
            label="_About"
            pixtype="stock"
            pixname="gtk-about" />
        </popup>
        '''
        verbs = [('CopyDate', self.copy_date),
                 ('CopyTime', self.copy_time),
                 ('Preferences', self.display_prefs),
                 ('About', self.display_about)]
        self.panel_applet.setup_menu(xml, verbs, self)
        return True

    def refresh_cfg(self):
        """
        Read the contents of the configuration file and update the clock
        accordingly. Tries to handle failures gracefully.
        """
        self.config.load()
        return

    def update_cfg(self,data):
        """
        Overwrites the timezone configuration file with the given data.
        """
        self.config.save(data)
        self.refresh_cfg()
        self.update_time()
        return

    def launch(self):
        """
        Construct the user-interface, stylize the widgets, connect the timers
        and so on. Basically; launch the applet.
        """
        # actually populate UI
        self.main_bttn = Gtk.ToggleButton(label="")
        if IS_GTK3:
            self.main_bttn.set_relief(Gtk.ReliefStyle.NONE)
        else:
            self.main_bttn.set_relief(Gtk.RELIEF_NONE)
        self.main_bttn.set_can_focus(False)
        self.main_bttn.set_name("TailsClockAppletButton")
        self.main_bttn.connect("button-press-event",self.popup_menu)
        self.main_bttn.connect("toggled",self.toggle_drop)
        # transparent background style
        if IS_GTK3:
            style_provider = Gtk.CssProvider()
            css = """
            #TailsClockAppletButton {
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
        else: # NOT_GTK3
            pass
        # add an instance of the calendar
        self.main_drop = TailsClockCalendarWindow(self.main_bttn)
        # add/show all
        self.panel_applet.add(self.main_bttn)
        self.panel_applet.show_all()
        self.refresh_cfg()
        self.update_time()
        return self

    def update_glib_timer(self):
        """
        Depending on whether we're showing seconds or not, schedule then
        next 'tick' appropriately. For example, if we're showing seconds
        then set timer to 1s, however, if not showing seconds; set timer
        to the number of seconds until next minute.
        """
        if self.glib_timer != None:
            GObject.source_remove(self.glib_timer)
            self.glib_timer = None
        if self.config.show_sec:
            self.glib_timer = GObject.timeout_add(1000,self.update_time)
        else:
            now = datetime.now()
            one_min = timedelta(minutes=1)
            delta = ((now + one_min) - now).seconds * 1000
            self.glib_timer = GObject.timeout_add(delta,self.update_time)
        return False

    def update_time(self):
        """
        Fired once-per second to update the time.
        """
        # get the date/time and apply tz_info to it
        utc_dt = datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        dt = utc_dt.astimezone(self.config.tz_info)
        # format the date/time stamp
        dt_format = self._dt_format()
        #debug_log("Format: "+dt_format)
        stamp = dt.strftime(dt_format)
        # actually update the label
        self.main_bttn.set_label(stamp)
        return self.update_glib_timer()

    def display_prefs(self,*argv):
        """
        Display the Tails Clock Preferences dialog.
        """
        TailsClockPrefsDialog(self).run()
        pass

    def display_about(self,*argv):
        TailsClockAboutDialog().run()
        pass

    def toggle_drop(self,widget):
        self.main_drop.toggle()
        return True

    def popup_menu(self,widget,event):
        """
        Trigger the context-menu to popup.
        """
        debug_log("popup_menu")
        if IS_GTK3:
            if event.button == 3 and (event.state & Gdk.ModifierType.MOD1_MASK) == 0:
                self.main_menu.popup(None,None,None,None,event.button,event.time)
                return True
        else: # NOT_GTK3
            if event.button == 3 and (event.state & Gdk.MOD1_MASK) == 0:
                self.main_menu.popup(None,None,None,event.button,event.time,None)
                return True
        if event.button > 1:
            return self.panel_applet.event(event)
        return False

    def copy_date(self,widget,event):
        cfg = self.config.copy()
        cfg.show_time = False
        cfg.show_dt = True
        cfg.show_yr = True
        dt_format = self._dt_format(cfg)
        utc_dt = datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        dt = utc_dt.astimezone(cfg.tz_info)
        stamp = dt.strftime(dt_format)
        debug_log("copy_date: "+dt_format+" -> "+stamp)
        display = Gdk.Display.get_default()
        clipboard = Gtk.Clipboard.get_for_display(display,Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(stamp,-1)
        clipboard.store()
        return True

    def copy_time(self,widget,event):
        cfg = self.config.copy()
        cfg.show_time = True
        cfg.show_tz = True
        cfg.show_dt = False
        cfg.show_yr = False
        dt_format = self._dt_format(cfg)
        utc_dt = datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        dt = utc_dt.astimezone(cfg.tz_info)
        stamp = dt.strftime(dt_format)
        debug_log("copy_time: "+dt_format+" -> "+stamp)
        display = Gdk.Display.get_default()
        clipboard = Gtk.Clipboard.get_for_display(display,Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(stamp,-1)
        clipboard.store()
        return True


tc_inst = None
def applet_factory(applet, iid, data = None, is_debug = False):
    """
    Construct the clock instance and launch it.
    """
    global IS_DEBUG
    IS_DEBUG = is_debug
    tc_inst = TailsClock(applet,iid,data).launch()
    return True
