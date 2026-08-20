# This script runs as a Morpheus remote task to update the Zabbix Server /etc/hosts file with the IP and Name of the provisioned VM
set -x
NAME="<%= server.name %>"
# Added sleep 10 to fix issue where IP address returns null when starting instance
sleep 10
IP="<%= server.externalIp %>"
MONITORING="<%= customOptions.enableMonitoring %>"

# Fail if IP is null or empty
if [ -z "$IP" ] || [ "$IP" = "null" ]; then
	echo "ERROR: IP address not available. Failing task to trigger retry."
	exit 1
fi

if [ $MONITORING = on ]
then
	echo "$IP $NAME" >> /etc/hosts
fi