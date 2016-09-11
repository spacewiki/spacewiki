#!/bin/bash
set -e
make syncdb
exec ./manage.py runserver -h 0.0.0.0 $@
