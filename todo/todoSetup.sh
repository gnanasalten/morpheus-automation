PGPass="<%=cypher.read('secret/postgres')%>"
DB_IP="<%=evars.DB_IP%>"
DB_PORT="<%=evars.DB_PORT%>"

#Update all packages with available update
apt-get update -y

#Install Postgres
sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
apt-get update -y
apt-get -y install postgresql-client-14

#apt install -y postgresql-client
export PGPASSWORD="<%=cypher.read('secret/postgres')%>"
psql -h $DB_IP -p $DB_PORT -U admin -d template1 -c "CREATE DATABASE todo;"
psql -h $DB_IP -p $DB_PORT -U admin -d template1 -c "CREATE USER todouser WITH PASSWORD '$PGPass';"
psql -h $DB_IP -p $DB_PORT -U admin -d template1 -c "grant all privileges on database todo to todouser;"
psql -h $DB_IP -p $DB_PORT -U admin -d todo -c "CREATE TABLE todos (item text);"
psql -h $DB_IP -p $DB_PORT -U admin -d todo -c "grant all privileges on table todos to todouser;"

mkdir -p /opt/todo
cat << EOF > /opt/todo/config.env
# POSTGRES CONFIG
PG_HOST=$DB_IP

# OPTIONAL TO OVERRIDE DEFAULTS
PG_PORT=$DB_PORT               # default is 5432
PG_USER=todouser               # default is postgres
PG_PASSWORD=$PGPass            # default is Password123?
PG_DATABASE=todo               # default is todos
#APP_SERVER_PORT=              # default is 8090
EOF