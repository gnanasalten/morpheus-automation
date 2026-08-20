# This shell script will install JSON server and configure it to serve the app.json file

IP="<%= server.internalIp %>"

apt update
#curl -sL https://deb.nodesource.com/setup_19.x | sudo bash -
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt install -y nodejs

cat <<EOF > /opt/jsonserver/package.json
{
  "name": "test-json-server",
  "version": "1.0.0",
  "description": "",
  "main": "",
  "dependencies": {},
  "scripts": {
    "start": "json-server --host $IP -p 8101 --watch /opt/jsonserver/app.json"
  },
  "author": "",
  "license": "ISC"
}
EOF

#Pinning version as latest version tested in May 2024 did not support multiple query parameters.
npm install -g json-server@1.0.0-alpha.23

cat <<EOF > /opt/jsonserver/jsctl.sh
#!/usr/bin/bash

# Function to start json-server
start_server() {
    echo "Starting json-server..."
    cd /opt/jsonserver
    (nohup npm start > /dev/null 2>&1 &)
    ps aux | grep '[n]pm start' | awk '{print \$2}' > npm-server.pid
    echo "json-server started"
}

# Function to stop json-server
stop_server() {
    if [ ! -f /opt/jsonserver/npm-server.pid ]; then
        echo "json-server is not running."
    else
        pkill -f json-server
        rm /opt/jsonserver/npm-server.pid
        echo "json-server stopped."
    fi
}

# Check the command-line argument
case \$1 in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
esac
EOF

chmod 744 /opt/jsonserver/jsctl.sh
/opt/jsonserver/jsctl.sh start
