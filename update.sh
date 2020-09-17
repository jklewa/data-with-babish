set -ex
wget localhost:5000/episodes?format=json -O ibdb.episodes.json -nv
wget localhost:5000/guests?format=json -O ibdb.guests.json -nv
wget localhost:5000/recipes?format=json -O ibdb.recipes.json -nv
wget localhost:5000/references?format=json -O ibdb.references.json -nv
wget localhost:5000/shows?format=json -O ibdb.shows.json -nv

PGPASSWORD=${POSTGRES_PASSWORD} PGUSER=${POSTGRES_USERNAME:-postgres} \
  PGHOST=${POSTGRES_HOSTNAME:-localhost} PGPORT=${POSTGRES_PORT:-54320} \
  pg_dump --dbname=babish_db --create --file=./ibdb/db_dump.sql

echo "Done"
