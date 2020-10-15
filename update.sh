set -ex
export HOSTNAME=0.0.0.0:5000

wget ${HOSTNAME}/episodes?format=json -O datasets/ibdb.episodes.json -nv
wget ${HOSTNAME}/guests?format=json -O datasets/ibdb.guests.json -nv
wget ${HOSTNAME}/recipes?format=json -O datasets/ibdb.recipes.json -nv
wget ${HOSTNAME}/references?format=json -O datasets/ibdb.references.json -nv
wget ${HOSTNAME}/shows?format=json -O datasets/ibdb.shows.json -nv

PGPASSWORD=${POSTGRES_PASSWORD:-postgres} PGUSER=${POSTGRES_USERNAME:-postgres} \
  PGHOST=${POSTGRES_HOSTNAME:-localhost} PGPORT=${POSTGRES_PORT:-54320} \
  pg_dump --dbname=babish_db --create --file=./ibdb/db_dump.sql

python utils/pg_dump_splitsort.py ibdb/db_dump.sql
cat ibdb/[0-9]*.sql > ibdb/db_dump.sql
rm ibdb/[0-9]*.sql

echo "Done"
