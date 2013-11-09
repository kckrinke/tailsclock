AUTOMAKE_OPTIONS=-Wno-portability
custom_files = \
	org.gnome.applets.TailsClock.panel-applet \
	org.gnome.panel.applet.TailsClock.service \
	TailsClock.server
CLEANFILES = $(custom_files)
EXTRA_DIST = \
	org.gnome.applets.TailsClock.panel-applet.in \
	org.gnome.panel.applet.TailsClock.service.in \
	TailsClock.server.in

appletdir = ${DESTDIR}${libdir}/gnome-applets
do_substitution = sed -e 's,[@]appletdir[@],$(appletdir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' 

.PHONEY: all

all:
	@$(do_substitution) < org.gnome.applets.TailsClock.panel-applet.in > org.gnome.applets.TailsClock.panel-applet
	@$(do_substitution) < org.gnome.panel.applet.TailsClock.service.in > org.gnome.panel.applet.TailsClock.service
	@$(do_substitution) < TailsClock.server.in > TailsClock.server

extraclean:
	-/bin/rm -fv config-tmp-*
	-/bin/rm -fv *~ \#*

clean:
	@[ -f org.gnome.applets.TailsClock.panel-applet ] && /bin/rm -v org.gnome.applets.TailsClock.panel-applet || true
	@[ -f org.gnome.panel.applet.TailsClock.service ] && /bin/rm -v org.gnome.panel.applet.TailsClock.service || true
	@[ -f TailsClock.server ] && /bin/rm -v TailsClock.server || true

install:
	@echo "Installing gnome-files to: ${DESTDIR}${datarootdir} and ${DESTDIR}${libdir}"
	@mkdir -p ${DESTDIR}${datarootdir}/gnome-panel/4.0/applets/
	@install -D -m 644 org.gnome.applets.TailsClock.panel-applet ${DESTDIR}${datarootdir}/gnome-panel/4.0/applets/
	@mkdir -p ${DESTDIR}${datarootdir}/dbus-1/services/
	@install -D -m 644 org.gnome.panel.applet.TailsClock.service ${DESTDIR}${datarootdir}/dbus-1/services/
	@mkdir -p ${DESTDIR}${libdir}/bonobo/servers/
	@install -D -m 644 TailsClock.server ${DESTDIR}${libdir}/bonobo/servers/

uninstall:
	@/bin/rm -v ${DESTDIR}${datarootdir}/gnome-panel/4.0/applets/org.gnome.applets.TailsClock.panel-applet
	@/bin/rm -v ${DESTDIR}${datarootdir}/dbus-1/services/org.gnome.panel.applet.TailsClock.service
	@/bin/rm -v ${DESTDIR}${libdir}/bonobo/servers/TailsClock.server
