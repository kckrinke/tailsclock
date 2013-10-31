DESTDIR := /
SUBDIRS = gnome locale src

clean: clean-recursive
	@$(foreach c,$(wildcard **/*.pyc),/bin/rm -v $c)
