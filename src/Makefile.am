
tailsclockdir = $(prefix)/lib/gnome-applets/
tailsclock = $(wildcard *.py)

EXTRA_DIST = $(tailsclock)

install:
	@install -D -m 644 TailsClockApplet.py $(tailsclockdir)
	@install -D -m 755 TailsClock-factory2.py $(tailsclockdir)
	@install -D -m 755 TailsClock-factory3.py $(tailsclockdir)
