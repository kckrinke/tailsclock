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

Currently, Tails Clock uses a hand-crafted Makefile as an interim build system.
Installation defaults to /opt though that's probably not "correct" for any
linux distribution. The following steps walk you through the installation.

```
# First step is to generate the files and translations
make DESTDIR=/usr
# Second step is to copy the files to the correct locations
sudo make install DESTDIR=/usr
# If you're installing this onto a GNOME2.x system, you'll need to logout
# and log back in, or restart the gnome-panel to see the new applet
```

Notice that the DESTDIR=/usr option is provided at each step. While this isn't
typical Makefile behaviour, this Makefile isn't setup via a ```./configure```
script either so please don't expect too much.

Try running ```make help``` to get some extra feedback on how to use the
Makefile as-is.

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

## TODO ##

- [ ] Implement a standards compliant build system
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
