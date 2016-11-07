#!/bin/bash
set -e

if [ $1 == "make" ]; then
  exec make $@
fi

exec ./manage.py $@
