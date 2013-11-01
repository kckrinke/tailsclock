#!/bin/bash
MESSAGES_POT=./locale/tailsclockapplet.pot
MESSAGES_PO=./locale/en/LC_MESSAGES/tailsclockapplet.po

echo -n "Generating POT... "
pygettext -o ${MESSAGES_POT} ./src/TailsClockApplet.py
echo "done"
echo -n "Creating EN PO... "
cat ${MESSAGES_POT} | \
    perl -e '$r="";while(my $l=<>){$r.=$l;};$r=~s!msgid "([^"]*)"(\s*\r??\n\s*msgstr) ""!msgid "$1"$2 "$1"!gms;$r=~s!CHARSET!UTF-8!g;print $r;' > ${MESSAGES_PO}
echo "done"