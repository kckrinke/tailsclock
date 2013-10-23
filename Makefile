#!/usr/bin/make

#
#: Simple build/install system for Tails Clock
#

DESTDIR:=/opt
PREFIX:=$(DESTDIR)

define _install_file
	@mkdir -vp $3;
	@cp -fv $2 $3;
	@chmod -v $1 $3/$2;
endef

all: mo in

help:
	@echo "# Tails Clock Makefile Usage #"
	@echo
	@echo "Variables:"
	@echo "  DESTDIR := $(DESTDIR)"
	@echo "    - Immediate installation target"
	@echo "  PREFIX := $(PREFIX)"
	@echo "    - Expected run-time install target"
	@echo
	@echo "'make help' - Display this text"
	@echo "'make all' - see mo,in"
	@echo "'make mo' - Generate machine readable language translations"
	@echo "'make in' - Configure template files for $(PREFIX)"
	@echo "'make pot' - Generate/Update language translation template"
	@echo "'make clean' - Clean source tree"
	@echo "'make install' - Install Tails Clock to prefix ($(DESTDIR))"
	@echo "'make uninstall' - Uninstall Tails Clock from prefix ($(DESTDIR))"

mo:
	@echo "Generating machine readable translation files..."
	@$(foreach p,$(wildcard ./locale/*/LC_MESSAGES/*.po), echo $p; [ -f $(basename $p) ] && rm -f $(basename $p); msgfmt --verbose --output-file $(basename $p).mo $p;)
	@echo "All translation files re-formatted."

in:
	@echo "Configuring template files..."
	@$(foreach i,$(wildcard *.in),sed -e "s#{{PREFIX}}#$(PREFIX)#" $(i) > $(basename $(i));echo "  $(i)";true;)
	@echo "Configuration of template files complete."

pot:
	@echo "Generating translation template..."
	@pygettext -o ./locale/messages.pot TailsClockApplet.py
	@echo "Translation template generated."

clean:
	@echo "Cleaning project sources..."
	@$(foreach m,$(wildcard ./locale/*/LC_MESSAGES/*.mo), rm -fv $m)
	@rm -fv *.pyc
	@$(foreach i,$(wildcard *.in),rm -fv $(basename $(i)); true;)
	@echo "Project is now clean."

install:
	@echo "Installing Tails Clock to $(DESTDIR)..."
	@$(call _install_file,644,org.gnome.applets.TailsClock.panel-applet,$(DESTDIR)/share/gnome-panel/4.0/applets/)
	@$(call _install_file,644,org.gnome.panel.applet.TailsClock.service,$(DESTDIR)/share/dbus-1/services/)
	@$(call _install_file,755,TailsClock-factory2.py,$(DESTDIR)/lib/gnome-applets/)
	@$(call _install_file,755,TailsClock-factory3.py,$(DESTDIR)/lib/gnome-applets/)
	@$(call _install_file,755,TailsClockApplet.py,$(DESTDIR)/lib/gnome-applets/)
	@$(call _install_file,644,TailsClock.server,$(DESTDIR)/lib/bonobo/servers/)
	@echo "Installing language translations to $(DESTDIR)/share/locale..."
	@$(foreach c,$(wildcard locale/*/LC_MESSAGES/*.mo), mkdir -pv $(DESTDIR)/share/$(shell sh -c "echo $(c) | sed -re 's/tailsclockapplet.mo//'"); cp -fv "$(c)" "$(DESTDIR)/share/$(c)"; chmod -v 644 "$(DESTDIR)/share/$(c)";)
	@echo "Install of the Tails Clock applet is complete."

uninstall:
	@echo "Removing installed files from $(DESTDIR) ..."
	@echo "(Note that this does not remove any paths.)"
	@rm -fv $(DESTDIR)/share/gnome-panel/4.0/applets/org.gnome.applets.TailsClock.panel-applet
	@rm -fv $(DESTDIR)/share/dbus-1/services/org.gnome.panel.applet.TailsClock.service
	@rm -fv $(DESTDIR)/lib/gnome-applets/TailsClock-factory2.py
	@rm -fv $(DESTDIR)/lib/gnome-applets/TailsClock-factory2.pyc
	@rm -fv $(DESTDIR)/lib/gnome-applets/TailsClock-factory3.py
	@rm -fv $(DESTDIR)/lib/gnome-applets/TailsClock-factory3.pyc
	@rm -fv $(DESTDIR)/lib/gnome-applets/TailsClockApplet.py
	@rm -fv $(DESTDIR)/lib/gnome-applets/TailsClockApplet.pyc
	@rm -fv $(DESTDIR)/lib/bonobo/servers/TailsClock.server
	@$(foreach m,$(wildcard $(DESTDIR)/share/locale/*/LC_MESSAGES/tailsclockapplet.mo), rm -fv $(m);)
