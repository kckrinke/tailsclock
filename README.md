# Tails Clock #

## Summary ##

This project is a simple GNOME panel applet for displaying the date and time.
There are very few configurable options, no weather reports or other fanciness.
Users can right-click on the applet, select the Preferences option and change
the Time Zone along with a few other general options from there. The timezone
is system-independent and is intended to allow the user to view the time in a
different Time Zone than the system settings.

## Purpose ##

The [Tails Project](https://tails.boum.org) has user privacy and anonymity set
as a very high priority. The current clock applet is entirely dependent upon
the locale of the system and users of Tails are typically getting confused by
the time being displayed in UTC. This simple applet is intended to solve that
problem for Tails users.

## Installing ##

Tails Clock uses autotools for configuration, building and installing. Simply
do the normal steps...

```
./configure --prefix /usr
make
sudo make install
```

## Hacking / Contributing ##

All help in maintaining this project is welcome.

For GNOME2.x development:
 * TailsClock-factory2.py is the actual applet loader script
 * The factory script is registered with bonobo via TailsClock.server

For GNOME3.x development:
 * TailsClock-factory3.py is the applet loader script
 * The factory script is registered with DBUS/GNOME via:
   * org.gnome.TailsClock.panel-applet
   * org.gnome.panel.applet.TailsClock.service

Translations:
 * from the top-level of the source tree, run gen-en-pot.sh to update the
   translations template (.pot), it'll also create the "EN" language from
   the template.
 * All current translations have been derived from free translation
   services found online.

## TODO ##

- [ ] Custom icons / artwork
- [ ] More / Update translations

## License / Copyright ##

```
Tails Clock - Simple GNOME panel applet clock.
Copyright (C) Kevin C. Krinke <kevin@krinke.ca>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
```
