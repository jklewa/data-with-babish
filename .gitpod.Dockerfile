FROM gitpod/workspace-postgres

USER gitpod

# for database
ENV PGUSERNAME=gitpod PGPASSWORD=postgres PGDATABASE=postgres
# for api.py
ENV POSTGRES_USERNAME=gitpod POSTGRES_PASSWORD=postgres POSTGRES_DBNAME=babish_db POSTGRES_PORT=5432

# need full repo for self-install
COPY . .
RUN pip install -r requirements.txt
