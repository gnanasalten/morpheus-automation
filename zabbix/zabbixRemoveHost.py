monitoring = morpheus["customOptions"]["enableMonitoring"]
authToken = morpheus["results"]["zabbixAPIToken"]

if monitoring == "on":
    import json
    import requests
    import sys

    #host = morpheus["customOptions"]["zabbixServer"]
    host = sys.argv[1]

    jbody = {
        "jsonrpc": "2.0",
        "method": "host.delete",
        "params": [
            morpheus["results"]["zabbixGetHost"]
        ],
        "id": 2
    }

    body = json.dumps(jbody)

    headers = {"Content-Type": "application/json-rpc", "Accept": "*/*", "Authorization": f"Bearer {authToken}"}
    url = "http://%s/zabbix/api_jsonrpc.php" % (host)

    response = requests.post(url, headers=headers, data=body, verify=False)
    if not response.ok:
        print("Error removing host: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")

    print("Host removed: Response code %s: %s" % (response.status_code, response.text))