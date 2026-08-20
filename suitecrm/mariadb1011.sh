RPass="<%=cypher.read('secret/mariaDBRootPass')%>"
MARIADB_VERSION="mariadb-10.11"

#Wait until any apt-get processes have finished
if [ `ps -ef | grep [a]pt-get | wc -l` = !0 ]
then
	sleep 120
fi

#Install MariaDB, start service and enable on boot
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup |sudo bash -s -- --mariadb-server-version="$MARIADB_VERSION"
apt update
apt-get install mariadb-server mariadb-client -y
systemctl stop mariadb.service
systemctl start mariadb.service
systemctl enable mariadb.service

#The following commands are from the mysql secure installation guidance
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$RPass';"
mysql -u root -p$RPass -e "FLUSH PRIVILEGES;"
mysql -u root -p$RPass -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -p$RPass -e "DELETE FROM mysql.user WHERE User='root' \ AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -u root -p$RPass -e "DROP DATABASE IF EXISTS test;"
mysql -u root -p$RPass -e "DELETE FROM mysql.db WHERE Db='test' \ OR Db='test\_%';"
mysql -u root -p$RPass -e "FLUSH PRIVILEGES;"

#Set bind-address parameter in my.cnf
sed -e '/^bind/s/^/#/g' -i /etc/mysql/mariadb.conf.d/50-server.cnf
systemctl restart mariadb.service