set -ex
wget localhost:5000/episodes?format=json -O ibdb.episodes.json -nv
wget localhost:5000/guests?format=json -O ibdb.guests.json -nv
wget localhost:5000/recipes?format=json -O ibdb.recipes.json -nv
wget localhost:5000/references?format=json -O ibdb.references.json -nv
wget localhost:5000/shows?format=json -O ibdb.shows.json -nv
echo "Done"
