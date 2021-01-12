#!/bin/sh

# If they is any error running the shell script, exit immediately
set -e
set -o errexit
set -o pipefail
set -o nounset

# Using proxy like nginx to serve static files
python manage.py collectstatic --noinput

# waiting for postgres to load before running
if [ -z "${POSTGRES_USER}" ]; then
    base_postgres_image_default_user='postgres'
    export POSTGRES_USER="${base_postgres_image_default_user}"
fi
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"

postgres_ready() {
python << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="db"
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo 'PostgreSQL is not available yet (sleeping)...'
  sleep 2
done

>&2 echo 'PostgreSQL is up - continuing...'

# This is the command that actually runs the application using uwsgi in production
uswgi --socket :8000 --master --enable-threads --module locallibrary.wsgi