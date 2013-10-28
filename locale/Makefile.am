LNGDIRS = de en es fr nl

MESSAGES_POT = en/LC_MESSAGES/tailsclockapplet.pot
MESSAGES_PO = en/LC_MESSAGES/tailsclockapplet.po

mo_files = $(foreach p,$(wildcard *.po),$(basename $(p)).mo;)
CLEANFILES = $(mo_files)
EXTRA_DIST = *.po *.pot
DESTDIR := $(prefix)

.PHONY: lngdirs $(LNGDIRS)
lngdirs: $(LNGDIRS)
$(LNGDIRS):
	@echo "Translating: $@/LC_MESSAGES/tailsclockapplet.po"
	@msgfmt --verbose --output-file $@/LC_MESSAGES/tailsclockapplet.mo $@/LC_MESSAGES/tailsclockapplet.po || true

all: $(LNGDIRS)

install:
	@$(foreach c,$(wildcard */LC_MESSAGES/*.mo),install -D -m 644 "$(c)" "$(DESTDIR)/share/locale/$(c)";)

uninstall:
	@$(foreach t,$(wildcard $(DESTDIR)/share/locale/*/LC_MESSAGES/tailsclockapplet.mo),rm -fv $(t);)
