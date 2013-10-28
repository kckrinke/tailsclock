EXTRA_DIST = $(wildcard *.py)
DESTDIR := ${prefix}

install:
	@echo "Installing src to: ${DESTDIR}${libdir}/gnome-applets/"
	@[ -d ${DESTDIR}${libdir}/gnome-applets/ ] || mkdir -p ${DESTDIR}${libdir}/gnome-applets/
	@install -D -m 644 TailsClockApplet.py ${DESTDIR}${libdir}/gnome-applets/
	@install -D -m 755 TailsClock-factory2.py ${DESTDIR}${libdir}/gnome-applets/
	@install -D -m 755 TailsClock-factory3.py ${DESTDIR}${libdir}/gnome-applets/

uninstall:
	@rm -f ${DESTDIR}${libdir}/gnome-applets/TailsClockApplet.py
	@rm -f ${DESTDIR}${libdir}/gnome-applets/TailsClock-factory2.py
	@rm -f ${DESTDIR}${libdir}/gnome-applets/TailsClock-factory3.py
