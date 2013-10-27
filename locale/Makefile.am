
MESSAGES_POT = en/LC_MESSAGES/tailsclock.pot

custom_files = $(foreach p,$(wildcard *.po),$(basename $(p)).mo;)
CLEANFILES = $(custom_files)
EXTRA_DIST = *.po *.pot

gen-pot:
	@pygettext -o $(MESSAGES_POT) ../src/TailsClockApplet.py

.po:
	@msgfmt --output-file $(basename $@).mo $@

install: .po
	@$(foreach c,$(wildcard */LC_MESSAGES/*.mo),\
		install -D -m 644 "$(c)" "$(prefix)/share/locale/$(c)"; \
	)
