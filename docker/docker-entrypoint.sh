#!/bin/bash
set -e

if [ $1 == "make" ]; then
  shift;
  exec make $@
fi

if [ -x $1 ]; then
  exec bash -c "$@"
fi

exec ./manage.py $@
