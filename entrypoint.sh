#!/bin/bash
python manage.py makemigrations
export PYTHONPATH=${PWD}
python manage.py migrate --check
status=$?
if [[ $status != 0 ]]; then
  python manage.py migrate
fi
python manage.py loaddata db.json
exec "$@"