#!/bin/bash
set -e

make syncdb
exec ./manage.py $@
