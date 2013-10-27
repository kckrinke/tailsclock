
custom_files = $(foreach p,$(wildcard *.in),$(basename $(p));)
CLEANFILES = $(custom_files)
EXTRA_DIST = *.in

appletdir = $(prefix)/lib/gnome-applets/

do_substitution = sed -e 's,[@]appletdir[@],$(appletdir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' 

.in: Makefile
	$(do_substitution) < $@ > $(basename $@)
	chmod 444 $(basename $@)

install:
	@install -D -m 644 org.gnome.applets.TailsClock.panel-applet \
		$(prefix)/share/gnome-panel/4.0/applets/
	@install -D -m 644 org.gnome.panel.applet.TailsClock.service \
		$(prefix)/share/dbus-1/services/
	@install -D -m 644 TailsClock.server \
		$(prefix)/lib/bonobo/servers/
