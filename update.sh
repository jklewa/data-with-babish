set -ex
wget localhost:5000/episodes?format=json -O datasets/ibdb.episodes.json -nv
wget localhost:5000/guests?format=json -O datasets/ibdb.guests.json -nv
wget localhost:5000/recipes?format=json -O datasets/ibdb.recipes.json -nv
wget localhost:5000/references?format=json -O datasets/ibdb.references.json -nv
wget localhost:5000/shows?format=json -O datasets/ibdb.shows.json -nv

PGPASSWORD=${POSTGRES_PASSWORD} PGUSER=${POSTGRES_USERNAME:-postgres} \
  PGHOST=${POSTGRES_HOSTNAME:-localhost} PGPORT=${POSTGRES_PORT:-54320} \
  pg_dump --dbname=babish_db --create --file=./ibdb/db_dump.sql

python utils/pg_dump_splitsort.py ibdb/db_dump.sql
cat ibdb/[0-9]*.sql > ibdb/db_dump.sql
rm ibdb/[0-9]*.sql

echo "Done"
