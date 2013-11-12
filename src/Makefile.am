AUTOMAKE_OPTIONS=-Wno-portability
EXTRA_DIST = $(wildcard *.py)

extraclean:
	-/bin/rm -fv config-tmp-*
	-/bin/rm -fv *~ \#*

install:
	@echo "Installing src to: ${DESTDIR}/lib/gnome-applets/"
	@mkdir -p ${DESTDIR}${prefix}/lib/gnome-applets/
	@install -D -m 644 TailsClockApplet.py ${DESTDIR}${prefix}/lib/gnome-applets/
	@install -D -m 755 TailsClock-factory2.py ${DESTDIR}${prefix}/lib/gnome-applets/
	@install -D -m 755 TailsClock-factory3.py ${DESTDIR}${prefix}/lib/gnome-applets/

uninstall:
	@/bin/rm -v ${DESTDIR}${prefix}/lib/gnome-applets/TailsClockApplet.py
	@/bin/rm -v ${DESTDIR}${prefix}/lib/gnome-applets/TailsClock-factory2.py
	@/bin/rm -v ${DESTDIR}${prefix}/lib/gnome-applets/TailsClock-factory3.py
