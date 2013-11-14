AUTOMAKE_OPTIONS=-Wno-portability
DESTDIR := /
SUBDIRS = gnome locale src

realclean: clean
	-/bin/rm -fv configure
	-/bin/rm -fv Makefile.in
	-/bin/rm -fv src/Makefile.in
	-/bin/rm -fv locale/Makefile.in
	-/bin/rm -fv gnome/Makefile.in

extraclean:
	for i in ${SUBDIRS}; do (cd $$i; $(MAKE) $(MFLAGS) extraclean); done
	-/bin/rm -fv config-tmp-*
	-/bin/rm -fv *~ \#*

clean: clean-recursive
	@$(foreach c,$(wildcard **/*.pyc),/bin/rm -v $c)
