RPass="<%=cypher.read('secret/mariaDBRootPass')%>"
ZDBPass="<%=cypher.read('secret/zDBPass')%>"

# Add the Zabbix repo
cd /tmp
file_url_zabbix="<%= archives.link('Automation Training Archive', 'zabbix-release_latest_7.2 ubuntu24.04_all.deb', 1200) %>"
wget $file_url_zabbix -O "./zabbix-release_latest_7.2 ubuntu24.04_all.deb" --no-check-certificate
dpkg -i zabbix-release_latest_7.2\ ubuntu24.04_all.deb
apt update

# Install MariaDB (At time of writing, Zabbix 7.2 recommends mariadb 11.4)
apt install software-properties-common -y
file_url_mariadb="<%= archives.link('Automation Training Archive', 'mariadb_repo_setup', 1200) %>"
wget $file_url_mariadb -O "./mariadb_repo_setup" --no-check-certificate
chmod +x mariadb_repo_setup
./mariadb_repo_setup  --mariadb-server-version="mariadb-11.4.2"
apt update
apt-get install mariadb-server mariadb-client -y

# Restart MariaDB and enable on boot
systemctl stop mariadb.service
systemctl start mariadb.service
systemctl enable mariadb.service

# Note that MariaDB authentication changed from version 10.4 - see https://mariadb.com/kb/en/authentication-from-mariadb-10-4/
# The following commands are from the mysql secure installation guidance
# Remove anonymous users
mariadb -e "DELETE FROM mysql.global_priv WHERE User='';"

# Disable remote root login
mariadb -e "DELETE FROM mysql.global_priv WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"

# Remove test database
mariadb -e "DROP DATABASE IF EXISTS test;"

# Remove privileges on test database
mariadb -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%'"

# Reload privileges table
mariadb -e "FLUSH PRIVILEGES;"

# Create the Zabbix database and user
mariadb -e "create database zabbix character set utf8mb4 collate utf8mb4_bin;"
mariadb -e "grant all privileges on zabbix.* to zabbix@localhost identified by '$ZDBPass';"
mariadb -e "set global log_bin_trust_function_creators = 1;"

# Import the initial schema and data
apt -y install zabbix-sql-scripts
zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mariadb --default-character-set=utf8mb4 -uzabbix -p$ZDBPass zabbix
mariadb -e "set global log_bin_trust_function_creators = 0;"

# Install Zabbix software
apt -y install zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-agent

# Add the Zabbix DB user password to the server config file
echo "DBPassword=$ZDBPass" >> /etc/zabbix/zabbix_server.conf

systemctl restart zabbix-server zabbix-agent
systemctl enable zabbix-server zabbix-agent
systemctl restart apache2
systemctl enable apache2