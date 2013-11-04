DESTDIR := /
SUBDIRS = gnome locale src

extraclean:
	for i in ${SUBDIRS}; do (cd $$i; $(MAKE) $(MFLAGS) extraclean); done
	-/bin/rm -fv config-tmp-*
	-/bin/rm -fv *~ \#*

clean: clean-recursive
	@$(foreach c,$(wildcard **/*.pyc),/bin/rm -v $c)
