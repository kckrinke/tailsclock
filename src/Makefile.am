
appletdir = $(prefix)/lib/gnome-applets/

EXTRA_DIST = $(wildcard *.py)

install:
	@install -D -m 644 TailsClockApplet.py $(appletdir)
	@install -D -m 755 TailsClock-factory2.py $(appletdir)
	@install -D -m 755 TailsClock-factory3.py $(appletdir)

uninstall:
	@rm -f $(appletdir)/TailsClockApplet.py
	@rm -f $(appletdir)/TailsClock-factory2.py
	@rm -f $(appletdir)/TailsClock-factory3.py
