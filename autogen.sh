#!/bin/sh

echo "Generating configure files... may take a while."

touch NEWS
autoreconf --install --force && rm -f NEWS && \
  echo "Preparing was successful if there was no error messages above." && \
  echo "Now type:" && \
  echo "  ./configure && make"  && \
  echo "Run './configure --help' for more information"
