#!/usr/bin/make

#
#: Simple build/install system for Tails Clock
#

DESTDIR:=/usr
PREFIX:=$(DESTDIR)

all: mo

help:
	@echo "Note: there is nothing to do for 'make all'."
	@echo
	@echo "'make mo' - Generate machine readable language translations"
	@echo "'make pot' - Generate/Update language translation template"
	@echo "'make clean' - Clean source tree"
	@echo "'make install' - Install Tails Clock to $(PREFIX)"

mo:
	@echo "Generating machine readable translation files..."
	@$(foreach p,$(wildcard ./locale/*/LC_MESSAGES/*.po), msgfmt --verbose --output-file $(basename $p).mo $p)
	@echo "All translation files re-formatted."

pot:
	@echo "Generating translation template..."
	@pygettext -o ./locale/messages.pot TailsClockApplet.py
	@echo "Translation template generated."

clean:
	@echo "Cleaning project sources..."
	@$(foreach m,$(wildcard ./locale/*/LC_MESSAGES/*.mo), rm -fv $m)
	@rm -fv *.pyc
	@echo "Project is now clean."

install:
	@mkdir -p $(PREFIX)/share/gnome-panel/4.0/applets/
	@cp -v org.gnome.applets.TailsClock.panel-applet $(PREFIX)/share/gnome-panel/4.0/applets/
	@mkdir -p $(PREFIX)/share/dbus-1/services/
	@cp -v org.gnome.panel.applet.TailsClock.service $(PREFIX)/share/dbus-1/services/
	@mkdir -p $(PREFIX)/lib/gnome-applets
	@cp -v TailsClock-factory2.py $(PREFIX)/lib/gnome-applets
	@cp -v TailsClock-factory3.py $(PREFIX)/lib/gnome-applets
	@cp -v TailsClockApplet.py $(PREFIX)/lib/gnome-applets
	@mkdir -p $(PREFIX)/lib/bonobo/servers/
	@cp -v TailsClock.server $(PREFIX)/lib/bonobo/servers/
	@mkdir -p $(PREFIX)/share/locale/de/LC_MESSAGES/
	@cp -v locale/de/LC_MESSAGES/tailsclockapplet.mo $(PREFIX)/share/locale/de/LC_MESSAGES/tailsclockapplet.mo
	@echo "Install of the Tails Clock applet is complete."

uninstall:
	@rm -fv $(PREFIX)/share/gnome-panel/4.0/applets/org.gnome.applets.TailsClock.panel-applet
	@rm -fv $(PREFIX)/share/dbus-1/services/org.gnome.panel.applet.TailsClock.service
	@rm -fv $(PREFIX)/lib/gnome-applets/TailsClock-factory2.py
	@rm -fv $(PREFIX)/lib/gnome-applets/TailsClock-factory3.py
	@rm -fv $(PREFIX)/lib/gnome-applets/TailsClockApplet.py
	@rm -fv $(PREFIX)/lib/bonobo/servers/TailsClock.server
	@rm -fv $(PREFIX)/share/locale/de/LC_MESSAGES/tailsclockapplet.mo
	@echo "Uninstall of the Tails Clock applet is complete."
