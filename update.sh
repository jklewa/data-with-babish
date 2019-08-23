set -ex
wget localhost:5000/episodes?format=json -O ibdb.episodes.json -q
wget localhost:5000/guests?format=json -O ibdb.guests.json -q
wget localhost:5000/recipes?format=json -O ibdb.recipes.json -q
wget localhost:5000/references?format=json -O ibdb.references.json -q
wget localhost:5000/shows?format=json -O ibdb.shows.json -q
echo "Done"
