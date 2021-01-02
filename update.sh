set -ex

docker-compose down
docker-compose up -d db
docker-compose run --rm ibdb sync update export

echo "Done"
