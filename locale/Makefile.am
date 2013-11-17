AUTOMAKE_OPTIONS=-Wno-portability
LNGDIRS = $(dir $(wildcard */))

mo_files = $(foreach p,$(wildcard *.po),$(basename $(p)).mo;)
CLEANFILES = $(mo_files)
EXTRA_DIST = *.po *.pot

.PHONY: lngdirs $(LNGDIRS)
lngdirs: $(LNGDIRS)
$(LNGDIRS):
	@echo "Translating: $@LC_MESSAGES/tailsclockapplet.po"
	@msgfmt --verbose --output-file $@LC_MESSAGES/tailsclockapplet.mo $@LC_MESSAGES/tailsclockapplet.po || true

all: $(LNGDIRS)

extraclean:
	@/bin/rm -fv config-tmp-* || true
	@/bin/rm -fv *~ \#* || true
	@/bin/rm -fv */LC_MESSAGES/*~ || true
	@/bin/rm -fv */LC_MESSAGES/\#* || true

clean:
	@$(foreach m,$(wildcard */LC_MESSAGES/*.mo),/bin/rm -v $(m);)

install:
	@echo "Installing locale to: ${DESTDIR}${datarootdir}/locale/"
	@$(foreach c,$(wildcard */LC_MESSAGES/*.mo),\
	mkdir -p $(shell dirname ${DESTDIR}${datarootdir}/locale/$(c));\
	install -T -D -m 644 "$(c)" ${DESTDIR}${datarootdir}/locale/$(c);)

uninstall:
	@$(foreach t,$(wildcard ${DESTDIR}${datarootdir}/locale/*/LC_MESSAGES/tailsclockapplet.mo),/bin/rm -v $(t);)
