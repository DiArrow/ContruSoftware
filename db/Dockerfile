FROM postgres:14.22

# Copiar modelo de datos al contenedord
COPY init/ /docker-entrypoint-initdb.d/

# Persistencia de datos
VOLUME /var/lib/postgresql/data

# Puero de entrada de la DB
EXPOSE 5432
