EXTRA_DIST = $(wildcard *.py)

extraclean:
	-/bin/rm -fv config-tmp-*
	-/bin/rm -fv *~ \#*

install:
	@echo "Installing src to: ${DESTDIR}${libdir}/gnome-applets/"
	@mkdir -p ${DESTDIR}${libdir}/gnome-applets/
	@install -D -m 644 TailsClockApplet.py ${DESTDIR}${libdir}/gnome-applets/
	@install -D -m 755 TailsClock-factory2.py ${DESTDIR}${libdir}/gnome-applets/
	@install -D -m 755 TailsClock-factory3.py ${DESTDIR}${libdir}/gnome-applets/

uninstall:
	@/bin/rm -v ${DESTDIR}${libdir}/gnome-applets/TailsClockApplet.py
	@/bin/rm -v ${DESTDIR}${libdir}/gnome-applets/TailsClock-factory2.py
	@/bin/rm -v ${DESTDIR}${libdir}/gnome-applets/TailsClock-factory3.py
