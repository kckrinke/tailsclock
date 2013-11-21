AUTOMAKE_OPTIONS=-Wno-portability
DESTDIR := /
SUBDIRS = gnome locale src

distclean: clean
	@echo "Removing auto generated files..."
	@/bin/rm -fv Makefile.in src/Makefile.in locale/Makefile.in gnome/Makefile.in || true
	@/bin/rm -fv Makefile src/Makefile locale/Makefile gnome/Makefile || true
	@/bin/rm -fv aclocal.m4 || true
	@/bin/rm -frv autom4te.cache/ || true
	@echo "Removing configure files"
	@/bin/rm -fv config.log || true
	@/bin/rm -fv config.status || true
	@/bin/rm -fv config.guess || true
	@/bin/rm -fv config.sub || true
	@/bin/rm -fv configure || true

extraclean:
	for i in ${SUBDIRS}; do (cd $$i; $(MAKE) $(MFLAGS) extraclean); done
	@/bin/rm -fv config-tmp-* || true
	@/bin/rm -fv *~ \#* || true

