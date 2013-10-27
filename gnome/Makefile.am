
custom_files = \
	org.gnome.applets.TailsClock.panel-applet \
	org.gnome.panel.applet.TailsClock.service \
	TailsClock.server
CLEANFILES = $(custom_files)
EXTRA_DIST = \
	org.gnome.applets.TailsClock.panel-applet.in \
	org.gnome.panel.applet.TailsClock.service.in \
	TailsClock.server.in

appletdir = $(prefix)/lib/gnome-applets

do_substitution = sed -e 's,[@]appletdir[@],$(appletdir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' 

.PHONEY: all

all:
	@$(do_substitution) < org.gnome.applets.TailsClock.panel-applet.in > org.gnome.applets.TailsClock.panel-applet
	@$(do_substitution) < org.gnome.panel.applet.TailsClock.service.in > org.gnome.panel.applet.TailsClock.service
	@$(do_substitution) < TailsClock.server.in > TailsClock.server

clean:
	@rm -f org.gnome.applets.TailsClock.panel-applet
	@rm -f org.gnome.panel.applet.TailsClock.service
	@rm -f TailsClock.server

install:
	@install -D -m 644 org.gnome.applets.TailsClock.panel-applet $(prefix)/share/gnome-panel/4.0/applets/
	@install -D -m 644 org.gnome.panel.applet.TailsClock.service $(prefix)/share/dbus-1/services/
	@install -D -m 644 TailsClock.server $(prefix)/lib/bonobo/servers/

uninstall:
	@rm -f $(prefix)/share/gnome-panel/4.0/applets/org.gnome.applets.TailsClock.panel-applet
	@rm -f $(prefix)/share/dbus-1/services/org.gnome.panel.applet.TailsClock.service
	@rm -f $(prefix)/lib/bonobo/servers/TailsClock.server
