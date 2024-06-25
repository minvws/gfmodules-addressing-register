#!/usr/bin/env bash

set -e

DB_HOST=${1:-localhost}
DB_USER=${2:-postgres}
DB_PASS=${3:-postgres}
DB_NAME=${4:-postgres}

export PGPASSWORD=$DB_PASS

psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f tools/seed.sql -q -o /dev/null
