# _IBDB_

### An interactive Babish database

Note: APIs have an optional `?format=json` variant with a more detailed view

 * http://localhost:5000/
 * http://localhost:5000/episodes
 * http://localhost:5000/guests
 * http://localhost:5000/recipes
 * http://localhost:5000/references
 * http://localhost:5000/shows

### Local Development

Required tools: [**Docker**](https://docs.docker.com/), [**Docker Compose**](https://docs.docker.com/compose/)

1. `cd data-with-babish/`
2. `docker-compose up -d --build`
3. Open http://localhost:5000/ to view the interactive read-only API

Notable files:

 * app.py - Source code for the interactive API
 * cli.py - Source code for the `ibdb` CLI
 * models.py - [SQLAlchemy](https://www.sqlalchemy.org/) ORM models
 * db_dump.sql - [pg_dump](https://www.postgresql.org/docs/10/app-pgdump.html) of the IBDB postgres database
 * populate_db.py - Upserts BWB episodes into the IBDB