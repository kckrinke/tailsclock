EXTRA_DIST = $(wildcard *.py)
DESTDIR := ${prefix}

install:
	@[ -d ${DESTDIR}/lib/gnome-applets/ ] || mkdir -p ${DESTDIR}/lib/gnome-applets/
	@install -D -m 644 TailsClockApplet.py ${DESTDIR}/lib/gnome-applets/
	@install -D -m 755 TailsClock-factory2.py ${DESTDIR}/lib/gnome-applets/
	@install -D -m 755 TailsClock-factory3.py ${DESTDIR}/lib/gnome-applets/

uninstall:
	@rm -f ${prefix}/lib/gnome-applets/TailsClockApplet.py
	@rm -f ${prefix}/lib/gnome-applets/TailsClock-factory2.py
	@rm -f ${prefix}/lib/gnome-applets/TailsClock-factory3.py
