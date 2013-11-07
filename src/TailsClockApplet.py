#!/usr/bin/env python
"""
Tails Clock Applet

A simple GNOME panel applet (GNOME 2.x or GNOME 3 in fallback/classic mode)
that displays the date and time. The clock applet defaults to UTC, however,
users can configure the timezone in the applet's preferences. Changing the
timezone in the applet does not affect any actual part of the operating
system with the exception of storing the currently selected timezone in
~/.config/tailsclock/timezone

Author: Kevin C. Krinke <kevin@krinke.ca>
License: GNU Public License 3.0 (or greater)

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

import tempfile
(LOG_FILE_DSC,LOG_FILE_PATH)=tempfile.mkstemp( suffix='.log',
                                               prefix='tailsclockapplet')

IS_DEBUG=False
def debug_log(message):
    global IS_DEBUG
    if not IS_DEBUG:
        return False
    sys.stderr.write("TailsClock: "+message+"\n")
    try:
        fh = open(LOG_FILE_PATH,"a")
        fh.write(message+"\n")
        fh.close()
    except Exception, e:
        sys.stderr.write("TailsClock: Exception caught: ("+str(e)+")\n")
    return True

#: load up Gtk
IS_GTK3=True
try:
    from gi.repository import Gtk, GObject, Gdk, PanelApplet
except: # Can't use ImportError, as gi.repository isn't quite that nice...
    IS_GTK3=False
    import gtk as Gtk
    import gobject as GObject
    import gtk.gdk as Gdk
    import gnomeapplet

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
            if data.has_key('show_tz'):
                self.show_tz = bool(data['show_tz'])
            if data.has_key('show_sec'):
                self.show_sec = bool(data['show_sec'])
            if data.has_key('show_12hr'):
                self.show_12hr = bool(data['show_12hr'])
            if data.has_key('show_yr'):
                self.show_yr = bool(data['show_yr'])
            if data.has_key('show_dt'):
                self.show_dt = bool(data['show_dt'])
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
            self._write_file("{0}\n".format(self.cfg_tz_path,data['tz']))
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

    def locale_supports_am_pm(self):
        am = locale.nl_langinfo(locale.AM_STR)
        if len(am) > 0:
            return True
        return False

    def get_show_am_pm(self):
        if self.locale_supports_am_pm():
            if self.show_12hr:
                return True
        return False

    def get_time_fmt(self):
        """
        Construct the strftime format string to render the time as-per the
        end-user's preferences. Will always return a valid strftime string.
        """
        locale.setlocale(locale.LC_NUMERIC,'POSIX')
        if self.get_show_am_pm():
            if self.show_sec and self.show_tz:
                #Translators: strftime to display the clock with seconds,
                # timezone and AM/PM format
                return _("%I:%M:%S %p %Z")
            if self.show_sec:
                #Translators: strftime to display the clock with seconds and
                # AM/PM format
                return _("%I:%M:%S %p")
            if self.show_tz:
                #Translators: strftime to display the clock with timezone and
                # AM/PM format
                return _("%I:%M %p %Z")
            #Translators: strftime to display the clock with AM/PM format (no
            # seconds or timezone)
            return _("%I:%M %p")
        if self.show_sec and self.show_tz:
            #Translators: strftime to display the clock with seconds, timezone
            # and 24hr format
            return _("%H:%M:%S %Z")
        if self.show_sec:
            #Translators: strftime to display the clock with seconds in 24hr
            # format
            return _("%H:%M:%S")
        if self.show_tz:
            #Translators: strftime to display the clock with timezone and 24hr
            # format
            return _("%H:%M %Z")
        #Translators: strftime to display the clock in 24hr format (no seconds
        # or timezone)
        return _("%H:%M")

    def get_date_fmt(self):
        """
        Construct the strftime format string to render the date as-per the
        end-user's preferences. If the user prefers that no date be show, this
        method will return None.
        """
        if self.show_dt:
            if self.show_yr:
                #Translators: long-form strftime representing the date and year
                #EN example: "Fri 01 Nov 2013"
                return _("%a %d %b %Y")
            #Translators: long-form strftime representing the date without the
            # year. EN example: "Fri 01 Nov"
            return _("%a %d %b")
        return None # Don't display the date

    def get_dt_fmt(self):
        """
        Returns the combination of date and time strftime strings into one
        string. If the user does not want to see the date, this will return just
        the time format string.
        """
        date_fmt = self.get_date_fmt()
        if date_fmt is not None:
            #Translators: combining date{0} with time{1}, reverse the {0} and
            # {1}. If you want to have the date come after the time.
            #EN example: "Fri 01 Nov 2013, 11:20 PM EDT"
            return _("{0}, {1}").format(date_fmt,self.get_time_fmt())
        return self.get_time_fmt()

    # internal method to write text to a file
    def _write_file(self,path,contents):
        try:
            fh = open(path,'w')
            fh.write(contents)
            fh.close()
        except Exception, e:
            debug_log("_write_file: " + str(e) + "\n")
            return False
        return True

    # internal method to write yaml to a file
    def _write_yaml(self,path,data):
        current = self._read_yaml(path)
        yaml = "# DO NOT EDIT - This file is overwritten automatically. #\n"
        for k in current.keys():
            if k is 'tz':
                next
            if data.has_key(k):
                yaml += k+": "+str(data[k])+"\n"
            else:
                yaml += k+": "+str(current[k])+"\n"
        return self._write_file(path,yaml)

    # internal method to read text from a file
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

    # internal method to read yaml from a file
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
            if re.match("^\s*$",line) or re.match("^\s*#",line):
                # ignore blank lines and #-comments
                continue
            line = re.sub("\s*#.*$","",line)
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
    show_24hr = None
    show_tz = None
    show_sec = None
    show_yr = None
    show_dt = None

    # internal method to add a preference checkbox in a consistent way
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
        self.panel_applet.refresh_cfg()
        #: initialize self
        if IS_GTK3:
            flags = Gtk.DialogFlags.MODAL
            buttons = (Gtk.STOCK_ABOUT,Gtk.ResponseType.ACCEPT,
                       Gtk.STOCK_CLOSE,Gtk.ResponseType.OK)
        else:
            flags = Gtk.DIALOG_MODAL | Gtk.DIALOG_NO_SEPARATOR
            buttons = (Gtk.STOCK_ABOUT,Gtk.RESPONSE_ACCEPT,
                       Gtk.STOCK_CLOSE,Gtk.RESPONSE_OK)
        #Translators: This is the title of the Preferences dialog window.
        Gtk.Dialog.__init__(self,_("Tails Clock Preferences"),
                            None,flags,buttons)
        self.set_modal(True)
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
        # General - Clock Format
        clock_fmt_hbox = Gtk.HBox()
        clock_fmt_frame = Gtk.Frame()
        clock_fmt_label = Gtk.Label()
        clock_fmt_frame.set_label_widget(clock_fmt_label)
        #Translators: Label for the clock format section of the prefs dialog
        clock_fmt_label.set_markup("<b>"+_("Clock Format")+"</b>")
        clock_fmt_inner_hbox = Gtk.HBox()
        clock_fmt_frame.add(clock_fmt_inner_hbox)
        clock_fmt_hbox.pack_start(clock_fmt_frame,True,True,8)
        if self.panel_applet.config.locale_supports_am_pm():
            debug_log("locale supports am/pm")
            tbl.pack_start(clock_fmt_hbox,True,True,8)
        self.show_12hr = Gtk.RadioButton()
        #Translators: label for the pref dialog: user wants to see AM/PM format
        # clock
        self.show_12hr.set_label(_("12 hour format"))
        clock_fmt_inner_hbox.pack_start(self.show_12hr,True,True,8)
        self.show_24hr = Gtk.RadioButton()
        self.show_24hr.join_group(self.show_12hr)
        #Translators: label for the pref dialog: user wants to see 24-hour
        # format clock
        self.show_24hr.set_label(_("24 hour format"))
        clock_fmt_inner_hbox.pack_start(self.show_24hr,True,True,8)
        if self.panel_applet.config.show_12hr:
            self.show_12hr.set_active(True)
            self.show_24hr.set_active(False)
        else:
            self.show_12hr.set_active(False)
            self.show_24hr.set_active(True)
        self.show_12hr.connect('toggled',self.update_general)
        self.show_24hr.connect('toggled',self.update_general)
        # General - Panel Section
        panel_dsp_hbox = Gtk.HBox()
        panel_dsp_frame = Gtk.Frame()
        panel_dsp_label = Gtk.Label()
        panel_dsp_frame.set_label_widget(panel_dsp_label)
        #Translators: Label for the panel-features section of the prefs dialog
        panel_dsp_label.set_markup("<b>"+_("Panel Display")+"</b>")
        panel_dsp_vbox = Gtk.VBox()
        panel_dsp_frame.add(panel_dsp_vbox)
        panel_dsp_hbox.pack_start(panel_dsp_frame,True,True,8)
        tbl.pack_start(panel_dsp_hbox,True,True,8)
        #Translators: label for the pref checkbox: users want to see the
        # timezone code (ie: UTC, EDT, etc)
        self.show_tz = self._add_pref_checkbox(
            panel_dsp_vbox,_("Display the timezone with the time"),
            self.panel_applet.config.show_tz,self.update_general)
        #Translators: label for the pref checkbox: users want to see the seconds
        # in the displayed time
        self.show_sec = self._add_pref_checkbox(
            panel_dsp_vbox,_("Show the seconds with the time"),
            self.panel_applet.config.show_sec,self.update_general)
        #Translators: label for the pref checkbox: users want to see the date in
        # the clock display
        self.show_dt = self._add_pref_checkbox(
            panel_dsp_vbox,_("Show the date with the time"),
            self.panel_applet.config.show_dt,self.toggled_dt)
        #Translators: label for the pref checkbox: users want to see the year in
        # the date portion of the clock
        self.show_yr = self._add_pref_checkbox(
            panel_dsp_vbox,_("When showing the date, show the year too"),
            self.panel_applet.config.show_yr,self.update_general)
        #Translators: name of the General tab in the preference dialog
        nbook.append_page(tbl,Gtk.Label(_("General")))
        #: Time Zone Configuration
        tz_vbox = Gtk.VBox()
        #Translators: name of the Timezone tab in the preference dialog
        nbook.append_page(tz_vbox,Gtk.Label(_("Timezone")))
        self.tz_store = Gtk.ListStore(str)
        self.tz_tview = Gtk.TreeView(self.tz_store)
        self.tz_tview.set_headers_visible(False)
        tz_rndrr = Gtk.CellRendererText()
        tz_col = Gtk.TreeViewColumn("tz_list", tz_rndrr, text = 0)
        self.tz_tview.append_column(tz_col)
        tz_scroll = Gtk.ScrolledWindow(hadjustment=None,vadjustment=None)
        if IS_GTK3:
            tz_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,
                                 Gtk.PolicyType.AUTOMATIC)
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
        if not self.panel_applet.config.locale_supports_am_pm():
            clock_fmt_hbox.set_sensitive(False)
        pass

    def close(self,widget,event):
        self.destroy()
        return True

    def update_general(self,*argv):
        data = DEFAULT_CFG_DATA.copy()
        data['show_12hr'] = self.show_12hr.get_active()
        data['show_sec'] = self.show_sec.get_active()
        data['show_tz'] = self.show_tz.get_active()
        data['show_yr'] = self.show_yr.get_active()
        data['show_dt'] = self.show_dt.get_active()
        self.panel_applet.update_cfg(data)
        pass

    def toggled_dt(self,widget):
        self.update_general()
        if self.show_dt.get_active():
            self.show_yr.set_sensitive(True)
        else:
            self.show_yr.set_sensitive(False)
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
        self.set_modal(True)
        #Translators: title for the about dialog
        self.set_name(_("Tails Clock"))
        #Translators: actual program name for the about dialog
        self.set_program_name(_("Tails Clock"))
        #Translators: the version string label for the about dialog. The
        # %s is replaced with the actual version number.
        self.set_version(_("Version %s") % "0.4")
        if IS_GTK3:
            self.set_license_type(Gtk.License.GPL_3_0)
        else:
            #Translators: This is the license notice displayed in the about
            # dialog. This particular string originates from the stock Gtk3
            # English-language license notice.
            self.set_license(_(
                "This program comes with ABSOLUTELY NO WARRANTY;"
                " for details, visit http://www.gnu.org/licenses/gpl.html"
                ))
        #Translators: This is the description found on the about dialog.
        self.set_comments(_("A simple GNOME panel applet clock"))
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
    http://stackoverflow.com/questions/11132929/showing-a-gtk-calendar-in-a-menu
    """
    panel_applet = None
    calendar = None
    def __init__(self,applet):
        self.panel_applet = applet
        if IS_GTK3:
            super(TailsClockCalendarWindow,
                  self).__init__(Gtk.WindowType.TOPLEVEL)
            self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        else:
            super(TailsClockCalendarWindow,self).__init__(Gtk.WINDOW_TOPLEVEL)
            self.set_type_hint(Gtk.gdk.WINDOW_TYPE_HINT_DOCK)
        self.set_decorated(False)
        self.set_resizable(False)
        self.stick()
        self.calendar = Gtk.Calendar()
        if IS_GTK3:
            self.calendar.set_display_options(
                Gtk.CalendarDisplayOptions.SHOW_WEEK_NUMBERS |
                Gtk.CalendarDisplayOptions.SHOW_HEADING |
                Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES
                )
        else:
            self.calendar.set_display_options(
                Gtk.CALENDAR_SHOW_WEEK_NUMBERS |
                Gtk.CALENDAR_SHOW_HEADING |
                Gtk.CALENDAR_SHOW_DAY_NAMES
                )
        cal_vbox = Gtk.VBox(False, 8)
        cal_hbox = Gtk.HBox(False, 8)
        self.add(cal_hbox)
        cal_hbox.pack_start(cal_vbox, True, False, 8)
        cal_vbox.pack_start(self.calendar, True, False, 8)
        pass

    def show_calendar(self):
        """
        Display the calendar widget and align it to the applet appropriately.
        """
        rect = self.panel_applet.main_bttn.get_allocation()
        main_window = self.panel_applet.main_bttn.get_toplevel()
        if IS_GTK3:
            [win_x, win_y] = main_window.get_window().get_root_coords(0,0)
        else: # NOT IS_GTK3
            [win_x, win_y] = main_window.get_window().get_origin()
        cal_x = win_x + rect.x
        cal_y = win_y + rect.y + rect.height
        self.show_all()
        [x, y] = self.apply_screen_coord_correction(
            cal_x, cal_y, self,
            self.panel_applet.main_bttn)
        debug_log("on_toggle: X:%d,Y:%d,WX:%d,WY:%d,CX:%d,CY:%d"
                  % (x,y,win_x,win_y,cal_x,cal_y))
        self.move(x, y)
        return True

    def hide_calendar(self):
        """
        Hide the widget
        """
        self.hide()
        return True

    def toggle(self):
        """
        Based on the state of the main clock button, hide or show the calendar
        widget appropriately.
        """
        if self.panel_applet.main_bttn.get_active():
            self.show_calendar()
        else:
            self.hide_calendar()
        return

    # This function "tries" to correct calendar window position so that it is
    # not obscured when a portion of main window is off-screen.
    # Known bug: If the main window is partially off-screen before Calendar
    # window has been realized then get_allocation() will return rect of 1x1 in
    # which case the calculations will fail & correction will not be applied
    def apply_screen_coord_correction(self, x, y, widget, relative_widget):
        w_rect = widget.get_allocation()
        r_rect = relative_widget.get_allocation()
        if self.panel_applet.orientation == TailsClock.ORIENT_RIGHT:
            corrected_y = y - r_rect.height
            corrected_x = x + r_rect.width
        elif self.panel_applet.orientation == TailsClock.ORIENT_LEFT:
            corrected_y = y - r_rect.height
            corrected_x = x - r_rect.width
        else:
            corrected_y = y
            corrected_x = x
        if IS_GTK3:
            screen_w = Gdk.Screen.get_default().get_width()
            screen_h = Gdk.Screen.get_default().get_height()
        else:
            screen_w = Gdk.screen_width()
            screen_h = Gdk.screen_height()
        delta_x = screen_w - (x + w_rect.width)
        delta_y = screen_h - (y + w_rect.height)
        if delta_x < 0:
            corrected_x += delta_x
        if corrected_x < 0:
            corrected_x = 0
        if delta_y < 0:
            corrected_y = y - w_rect.height - r_rect.height
        if corrected_y < 0:
            corrected_y = 0
        return [corrected_x, corrected_y]


class TailsClock:
    """
    Actual class used to manage the applet and display the time.
    """
    main_obox = None
    main_bttn = None
    main_label = None
    main_menu = None
    main_drop = None #Currently just a Calendar

    ORIENT_TOP = 0
    ORIENT_BOTTOM = 1
    ORIENT_LEFT = 2
    ORIENT_RIGHT = 3

    orientation = -1

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
        Simple initialization of the class instance. Call the launch() method
        to actuall launch the applet.
        """
        if IS_GTK3:
            debug_log("IS_GTK3")
        else:
            debug_log("NOT_GTK3")
        # live or debug?
        if applet.__class__ is not Gtk.Window:
            applet.set_background_widget(applet)
            applet.connect('change-orient',self.on_orient_change)
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

    # internal method to add Gtk3 menu items consistently
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
        #Translators: label for the context-menu option to copy the date to the
        # clipboard
        self._add_menu3_item(_("Copy Date"),Gtk.STOCK_COPY,
                             self.copy_date,self.main_menu)
        #Translators: label for the context-menu option to copy the time to the
        # clipboard
        self._add_menu3_item(_("Copy Time"),Gtk.STOCK_COPY,
                             self.copy_time,self.main_menu)
        self._add_menu3_item(None,Gtk.STOCK_PREFERENCES,
                             self.display_prefs,self.main_menu)
        self._add_menu3_item(None,Gtk.STOCK_ABOUT,
                             self.display_about,self.main_menu)
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
        #These strings are not user-visible, they're just
        #verbs for the menu system.
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
        self.main_obox = Gtk.Box()
        self.main_label = Gtk.Label("")
        self.main_bttn = Gtk.ToggleButton()
        self.main_bttn.add(self.main_label)
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
        self.main_drop = TailsClockCalendarWindow(self)
        # add/show all
        self.main_obox.add(self.main_bttn)
        self.panel_applet.add(self.main_obox)
        self.panel_applet.show_all()
        self.on_orient_change()
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
        Recursive callback event loop to update the time every second if
        the end-user has the seconds being displayed with the time, or
        once per minute at the start of the minute.
        """
        # get the date/time and apply tz_info to it
        utc_dt = datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        dt = utc_dt.astimezone(self.config.tz_info)
        # format the date/time stamp
        dt_format = self.config.get_dt_fmt()
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

    def display_about(self,*argv):
        """
        Display the About dialog.
        """
        TailsClockAboutDialog().run()
        pass

    def toggle_drop(self,*argv):
        """
        Toggle the drop-down widgets (currently just a calendar).
        """
        self.main_drop.toggle()
        return True

    def popup_menu(self,widget,event):
        """
        Trigger the context-menu to popup.
        """
        if IS_GTK3:
            if ((event.button == 3)
                and (event.state & Gdk.ModifierType.MOD1_MASK) == 0):
                self.main_menu.popup(None,None,None,None,
                                     event.button,event.time)
                return True
        if event.button > 1:
            return self.panel_applet.event(event)
        return False

    def copy_date(self,widget,event,data=None):
        """
        Get just the date part of the current configuration and copy it to
        the Gtk Clipboard.
        """
        cfg = self.config.copy()
        cfg.show_dt = True
        dt_format = cfg.get_date_fmt()
        utc_dt = datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        dt = utc_dt.astimezone(cfg.tz_info)
        stamp = dt.strftime(dt_format)
        debug_log("copy_date: "+dt_format+" -> "+stamp)
        if IS_GTK3:
            display = Gdk.Display.get_default()
            clipboard = Gtk.Clipboard.get_for_display(display,
                                                      Gdk.SELECTION_CLIPBOARD)
        else: # NOT IS_GTK3
            clipboard = self.panel_applet.get_clipboard(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(stamp,-1)
        clipboard.store()
        return True

    def copy_time(self,widget,event,data=None):
        """
        Get just the time part of the current configuration and copy it to
        the Gtk Clipboard.
        """
        cfg = self.config.copy()
        dt_format = cfg.get_time_fmt()
        utc_dt = datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        dt = utc_dt.astimezone(cfg.tz_info)
        stamp = dt.strftime(dt_format)
        debug_log("copy_time: "+dt_format+" -> "+stamp)
        if IS_GTK3:
            display = Gdk.Display.get_default()
            clipboard = Gtk.Clipboard.get_for_display(display,
                                                      Gdk.SELECTION_CLIPBOARD)
        else: # NOT IS_GTK3
            clipboard = self.panel_applet.get_clipboard(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(stamp,-1)
        clipboard.store()
        return True

    # internal method to handle ORIENT_UP changes
    def _set_applet_horiz_up(self):
        debug_log("orientation: horizontal")
        self.orientation = TailsClock.ORIENT_TOP
        if self.main_label.get_angle() != 0:
            self.main_label.set_angle(0)
        if IS_GTK3:
            self.main_obox.set_orientation(Gtk.Orientation.HORIZONTAL)
        else:
            self.main_obox.set_orientation(Gtk.ORIENTATION_HORIZONTAL)
        pass

    # internal method to handle ORIENT_DOWN changes
    def _set_applet_horiz_down(self):
        debug_log("orientation: horizontal")
        self.orientation = TailsClock.ORIENT_BOTTOM
        if self.main_label.get_angle() != 0:
            self.main_label.set_angle(0)
        if IS_GTK3:
            self.main_obox.set_orientation(Gtk.Orientation.HORIZONTAL)
        else:
            self.main_obox.set_orientation(Gtk.ORIENTATION_HORIZONTAL)
        pass

    # internal method to handle ORIENT_LEFT changes
    def _set_applet_vert_left(self):
        debug_log("orientation: vert left")
        self.orientation = TailsClock.ORIENT_LEFT
        if self.main_label.get_angle() != 270:
            self.main_label.set_angle(270)
        if IS_GTK3:
            self.main_obox.set_orientation(Gtk.Orientation.VERTICAL)
        else:
            self.main_obox.set_orientation(Gtk.ORIENTATION_VERTICAL)
        pass

    # internal method to handle ORIENT_RIGHT changes
    def _set_applet_vert_right(self):
        debug_log("orientation: vert right")
        self.orientation = TailsClock.ORIENT_RIGHT
        if self.main_label.get_angle() != 90:
            self.main_label.set_angle(90)
        if IS_GTK3:
            self.main_obox.set_orientation(Gtk.Orientation.VERTICAL)
        else:
            self.main_obox.set_orientation(Gtk.ORIENTATION_VERTICAL)
        pass

    def on_orient_change(self,orient=None,data=None):
        """
        React to orientation change events. Only relevant for actual panel
        applet use. The -d debug mode has no orientation change compliment
        to the actual gnome-panel's orientation changing ability.
        """
        if self.panel_applet.__class__ is not Gtk.Window:
            orientation = self.panel_applet.get_orient()
            if IS_GTK3:
                if orientation == PanelApplet.AppletOrient.UP:
                    # top panel
                    self._set_applet_horiz_up()
                elif orientation == PanelApplet.AppletOrient.DOWN:
                    # bottom panel
                    self._set_applet_horiz_down()
                elif orientation == PanelApplet.AppletOrient.LEFT:
                    # right-hand side of screen
                    self._set_applet_vert_left()
                elif orientation == PanelApplet.AppletOrient.RIGHT:
                    # left-hand side of screen
                    self._set_applet_vert_right()
            else:
                if orientation == gnomeapplet.ORIENT_UP:
                    # top of screen
                    self._set_applet_horiz_up()
                elif orientation == gnomeapplet.ORIENT_DOWN:
                    # bottom of screen
                    self._set_applet_horiz_down()
                elif orientation == gnomeapplet.ORIENT_LEFT:
                    # right-hand side
                    self._set_applet_vert_left()
                elif orientation == gnomeapplet.ORIENT_RIGHT:
                    # left-hand side of screen
                    self._set_applet_vert_right()
        return True
    


tc_inst = None
def applet_factory(applet, iid, data = None, is_debug = False):
    """
    Construct the clock instance and launch it.
    """
    global IS_DEBUG
    IS_DEBUG = is_debug
    if IS_DEBUG:
        #: log std{err,out} to the debug log
        sys.stdout = open(LOG_FILE_PATH,"a",0)
        sys.stderr = open(LOG_FILE_PATH,"a",0)
    tc_inst = TailsClock(applet,iid,data).launch()
    return True

