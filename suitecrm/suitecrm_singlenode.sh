RPass="<%=cypher.read('secret/mariaDBRootPass')%>"
SCRMDb="<%=customOptions.databaseNameSCRM%>"
SCRMUser="<%=customOptions.databaseUserSCRM%>"
SCRMPass="<%=customOptions.databasePassSCRM%>"
PHP_VERSION="8.1"
MARIADB_VERSION="mariadb-10.11"

#Wait until any apt-get processes have finished
if [ `ps -ef | grep [a]pt-get | wc -l` = !0 ]
then
    sleep 120
fi

#Install apache, start service and enable on boot
apt-get install apache2 -y
systemctl stop apache2.service
systemctl start apache2.service
systemctl enable apache2.service

#Install MariaDB, start service and enable on boot
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | sudo bash -s -- --mariadb-server-version="$MARIADB_VERSION"

apt update
apt-get install mariadb-server mariadb-client -y
systemctl stop mariadb.service
systemctl start mariadb.service
systemctl enable mariadb.service

#The following commands are from the mysql secure installation guidance
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$RPass';"
mysql -u root -p$RPass -e "FLUSH PRIVILEGES;"
mysql -u root -p$RPass -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -p$RPass -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -u root -p$RPass -e "DROP DATABASE IF EXISTS test;"
mysql -u root -p$RPass -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';"
mysql -u root -p$RPass -e "FLUSH PRIVILEGES;"

#Create the SuiteCRM User
mysql -u root -p$RPass -e "CREATE User '$SCRMUser'@'localhost' IDENTIFIED BY '$SCRMPass';"

#Create the SuiteCRM database
mysql -u root -p$RPass -e "CREATE DATABASE $SCRMDb;"
mysql -u root -p$RPass -e "GRANT ALL ON $SCRMDb.* TO $SCRMUser@localhost IDENTIFIED BY '$SCRMPass';"
mysql -u root -p$RPass -e "FLUSH PRIVILEGES;"

#Install required software for SuiteCRM
add-apt-repository ppa:ondrej/php -y
apt-get update
apt-get install php$PHP_VERSION libapache2-mod-php$PHP_VERSION \
php$PHP_VERSION-common php$PHP_VERSION-mysql php$PHP_VERSION-gmp \
php$PHP_VERSION-curl php$PHP_VERSION-intl php$PHP_VERSION-mbstring \
php$PHP_VERSION-xmlrpc php$PHP_VERSION-gd php$PHP_VERSION-bcmath \
php$PHP_VERSION-imap php$PHP_VERSION-xml php$PHP_VERSION-cli \
php$PHP_VERSION-zip -y

#Update php.ini file with required settings
short_open_tag=On
memory_limit=256M
upload_max_filesize=100M
max_execution_time=360

for key in short_open_tag memory_limit upload_max_filesize max_execution_time
do
    sed -i "s/^\($key\).*/\1 $(eval echo = \${$key})/" /etc/php/$PHP_VERSION/apache2/php.ini
done

#Restart apache
systemctl restart apache2.service

#Test file created for debugging
echo "<?php phpinfo( ); ?>" | sudo tee /var/www/html/phpinfo.php

#Download and install SuiteCRM
file_url="<%= archives.link('Automation Training Archive', 'SuiteCRM-7.14.3.zip', 1200) %>"
wget $file_url -O "./SuiteCRM-7.14.3.zip" --no-check-certificate
apt-get install unzip -y
unzip SuiteCRM-7.14.3.zip -d /var/www/html
mv /var/www/html/SuiteCRM-7.14.3/ /var/www/html/suitecrm

cd /var/www/html/suitecrm
chown -R www-data:www-data /var/www/html/suitecrm/
chmod -R 755 /var/www/html/suitecrm