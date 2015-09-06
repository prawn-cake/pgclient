FROM postgres
MAINTAINER Maksim Ekimovskii <ekimovsky.maksim@gmail.com>

# Default user is postgres
# ENV POSTGRES_PASSWORD: test

# This dir is supported by official postgresql image
# ENV PSQL_ENTRYPOINT /docker-entrypoint-initdb.d

RUN echo "CREATE DATABASE test WITH OWNER postgres;" >> $PSQL_ENTRYPOINT/create_db.sql