import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Variables
HOST = morpheus["morpheus"]["applianceHost"]
TOKEN = morpheus["morpheus"]["apiAccessToken"]
CLOUD_INIT_PASSWORD = "Password123?"
WINDOWS_PASSWORD = "Password123?"

## Request headers
HTTP_HEADERS = {"Content-Type":"application/json","Accept":"application/json","Authorization": "BEARER " + (TOKEN)}
HTTP_UPLOAD_HEADERS = {"Authorization": "BEARER " + (TOKEN)}



def get_repo_id_by_name(repo_name):
    url = "https://%s/api/options/codeRepositories" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting repo '%s': Response code %s: %s" % (repo_name, response.status_code, response.text))

    data = response.json()

    for repo in data["data"]:
        if repo_name in repo["name"]:
            return repo["value"]

    raise Exception("Searched %s repos. Repo '%s' not found..." % (len(data["data"]), repo_name))



def create_credential(name, password):
    url = "https://%s/api/credentials" % (HOST)
    jbody = {
      "credential": {
        "type": "username-password",
        "integration": {
        },
        "name": name,
        "enabled": True,
        "username": "morpheusci",
        "password": password
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding credential: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Credential %s added" % (name))
    cred_id = data["credential"]["id"]
    return cred_id



def get_cred_id_by_name(cred_name):
    url = "https://%s/api/credentials" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting credential '%s': Response code %s: %s" % (cred_name, response.status_code, response.text))

    data = response.json()

    for cred in data["credentials"]:
        if cred["name"] == cred_name:
            return cred["id"]

    raise Exception("Searched %s creds. Cred '%s' not found..." % (len(data["data"]), cred_name))



def add_task(name, code, id, script_code, sudo, source_type, repo_id, content_path, content_ref, execute_target):
    url = "https://%s/api/tasks" % (HOST)
    jbody = {
      "task": {
        "name": name,
        "code": code,
        "resultType": "value",
        "taskType": {
          "id": id,
          "code": script_code
        },
        "taskOptions": {
          "shell.sudo": sudo
        },
        "file": {
          "sourceType": source_type,
          "repository": {
            "id": repo_id
          },
          "contentPath": content_path,
          "contentRef": content_ref
        },
        "executeTarget": execute_target,
        "retryable": False,
        "allowCustomConfig": False
      }
    }    
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding task: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Task %s added" % (name))
    return data["task"]["id"]



def add_task_remote(name, code, id, script_code, sudo, remote_host, remote_port, source_type, repo_id, content_path, content_ref, execute_target,cred_id):
    url = "https://%s/api/tasks" % (HOST)
    jbody = {
      "task": {
        "name": name,
        "code": code,
        "taskType": {
          "id": id,
          "code": script_code
        },
        "taskOptions": {
          "shell.sudo": sudo,
          "host": remote_host,
          "port": remote_port
        },
        "file": {
          "sourceType": source_type,
          "repository": {
            "id": repo_id
          },
          "contentPath": content_path,
          "contentRef": content_ref
        },
        "executeTarget": execute_target,
        "credential": {
          "id": cred_id
        },
        "retryable": False,
        "allowCustomConfig": False
      }
    }    
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding task: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Task %s added" % (name))



def add_python_task(name, code, id, script_code, result_type, source_type, repo_id, content_path, content_ref, pythonargs, packages):
    url = "https://%s/api/tasks" % (HOST)
    jbody = {
      "task": {
        "name": name,
        "code": code,
        "taskType": {
          "id": id,
          "code": script_code
        },
        "resultType": result_type,
        "file": {
          "sourceType": source_type,
          "repository": {
            "id": repo_id
          },
          "contentPath": content_path,
          "contentRef": content_ref
        },
        "taskOptions": {
          "pythonArgs": pythonargs,
          "pythonAdditionalPackages": packages
        },
        "executeTarget": "local",
        "retryable": False,
        "allowCustomConfig": False
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding python task: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Python Task %s added" % (name))



def add_library_task(name, code, templateid):
    url = "https://%s/api/tasks" % (HOST)
    jbody = {
      "task": {
        "name": name,
        "code": code,
        "taskType": {
          "id": 3,
          "code": "containerTemplate"
        },
        "resultType": "value",
        "taskOptions": {
          "containerTemplate": templateid
        },
        "executeTarget": "resource",
        "retryable": False,
        "allowCustomConfig": False
      }
    }
    
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding library task: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Library task %s added" % (name))
    return data["task"]["id"]



def add_script_template(name, script_type, script_phase, script, runas, sudo):
    url = "https://%s/api/library/container-scripts" % (HOST)
    jbody = {
      "containerScript": {
        "name": name,
        "scriptType": script_type,
        "scriptPhase": script_phase,
        "script": script,
        "runAsUser": runas,
        "sudoUser": sudo
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding script template: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Script template %s added" % (name))



def create_file_template(file_content, phase, name, filename, filepath, fileowner, settingname, settingcategory):

    json_file = open(file_content, mode='r')
    json_content = json_file.read()
    json_file.close()

    url = "https://%s/api/library/container-templates" % (HOST)
    jbody = {
      "containerTemplate": {
        "templatePhase": phase,
        "name": name,
        "fileName": filename,
        "filePath": filepath,
        "template": json_content,
        "fileOwner": fileowner,
        "settingName": settingname,
        "settingCategory": settingcategory
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding template: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Template %s added" % (name))



def create_cypher_secret(key, ttl, value):
    url = "https://%s/api/cypher/v1/secret/%s?type=string&ttl=%s" % (HOST, key, ttl)
    jbody = {
      "value": value
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding cypher: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Cypher %s added" % (key))



#def get_vi_id_by_name(vi_name):
#    url = "https://%s/api/virtual-images?filterType=Synced&imageType=vmware" % (HOST)
#
#    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
#    if not response.ok:
#        raise Exception("Error getting virtual image '%s': Response code %s: %s" % (vi_name, response.status_code, response.text))
#
#    data = response.json()
#
#    for vi in data["virtualImages"]:
#        if vi["name"] == vi_name:
#            return vi["id"]
#
#    #NVR - fails on credentials - keyerror
#    #raise Exception("Searched %s virtual images. Virtual image '%s' not found..." % (len(data["credentials"]), vi_name))
#
#
#
##If adding a template to the node type, this is expected as an integer.
##Including this in the jbody above causes an issue when builing node types that do not have file templates as it expects an integer id.
##The if statement below adds in the relevant API components for adding a template to the node type only if a templateid is provided.
#     
#    if templateid:
#        jbody["containerType"]["templates"] = [templateid]
#    
#    body = json.dumps(jbody)
#
#    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
#    if not response.ok:
#        print("Error creating node type: Response code %s: %s" % (response.status_code, response.text))
#        raise Exception("Request error occured")
#    data = response.json()
#    print("Node Type %s added" % (name))



#def get_node_type_id_name(ct_name):
#    url = "https://%s/api/library/container-types" % (HOST)
#
#    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
#    if not response.ok:
#        raise Exception("Error getting node type '%s': Response code %s: %s" % (ct_name, response.status_code, response.text))
#
#    data = response.json()
#
#    for ct in data["containerTypes"]:
#        if ct["name"] == ct_name:
#            return ct["id"]
#
#    #NVR
#    #raise Exception("Searched %s container types. Container type '%s' not found..." % (len(data["credentials"]), ct_name))



def get_file_template_id_name(file_template_name):
    url = "https://%s/api/library/container-templates" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting file template '%s': Response code %s: %s" % (file_template_name, response.status_code, response.text))

    data = response.json()

    for ft in data["containerTemplates"]:
        if ft["name"] == file_template_name:
            return ft["id"]

    raise Exception("Searched %s file templates. FIle template '%s' not found..." % (len(data["containerTemplates"]), file_template_name))



def get_workflow_id_by_name(workflow_name):
    url = "https://%s/api/task-sets" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting workflow '%s': Response code %s: %s" % (workflow_name, response.status_code, response.text))

    data = response.json()

    for workflow in data["taskSets"]:
        if workflow["name"] == workflow_name:
            return workflow["id"]

    return 0



def add_workflow(workflow_name, taskid1, phase1, taskid2, phase2, taskid3, phase3):
    workflow_id = get_workflow_id_by_name(workflow_name)
    if workflow_id:
      print("Found existing workflow '%s', with workflow id %s..." % (workflow_name, workflow_id))
      return workflow_id

    url = "https://%s/api/task-sets" % (HOST)
    jbody = {
      "taskSet": {
        "name": workflow_name,
        "type": "provision",
        "tasks": [
          {
            "taskId": taskid1,
            "taskPhase": phase1
          },
          {
            "taskId": taskid2,
            "taskPhase": phase2
          },
          {
            "taskId": taskid3,
            "taskPhase": phase3
          }
        ]
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding workflow: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")

    data = response.json()
    print("Workflow '%s' added" % (workflow_name))

    return data["taskSet"]["id"]



## Main

## Get Git repo id - Tested
repo_id = get_repo_id_by_name("automation-class")

## Module 3 - Add task to dump variables - Tested
add_python_task("Dump Variables", "dumpVar", "22", "jythonTask", "value", "repository", repo_id, "dumpVariables.py", "main", "", "")

## Module 7 - Create Cyphers - Tested
create_cypher_secret("mariaDBRootPass", "0", "Password123?")
create_cypher_secret("zDBPass", "0", "Password123?")
create_cypher_secret("zAdminPass", "0", "zabbix")
create_cypher_secret("zAPIPass", "0", "Password123?")

## Module 7 - Create File Templates - Tested
create_file_template("zabbix/zabbix_frontend_config_aio", "preProvision", "Zabbix Frontend Config - AIO", "zabbix.conf.php", "/etc/zabbix/web", "www-data", "zabbix_fe_conf_aio", "Web")

## Module 7 - Create Tasks - Tested
add_task("Zabbix Install - AIO", "zabbixInstallAIO", "1", "script", "on", "repository", repo_id, "/zabbix/zabbixAIOInstall.sh", "main", "resource")
add_task("Zabbix Set Permissions - AIO", "zabbixSetPermAIO", "1", "script", "on", "repository", repo_id, "/zabbix/zabbixAIOSetPerms.sh", "main", "resource")
add_python_task("Zabbix Create API User", "zabbixCreateAPIUser", "22", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixCreateAPIUser.py", "main", "<%= cypher.read('secret/zAdminPass',true) %> <%= cypher.read('secret/zAPIPass',true) %>", "requests")
add_task("Zabbix Get Server IP", "zabbixServerIP", "1", "script", "", "repository", repo_id, "/zabbix/zabbixGetServerIP.sh", "main", "resource")
add_python_task("Zabbix Create Cypher Server IP", "zabbixCreateCypherServerIP", "22", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixCreateCypherServerIP.py", "main", "", "requests")
add_python_task("Zabbix Delete Cypher Server IP", "zabbixDeleteCypherServerIP", "22", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixDeleteCypherServerIP.py", "main", "", "requests")

## Create credential for remote tasks - Tested
create_credential("morpheusci", "M0rph@dmin")
cred_id = get_cred_id_by_name("morpheusci")

## Add tasks and templates for Zabbix Agent Install - Tested
add_task("Zabbix Agent Install", "zabbixAgentInstall", "1", "script", "on", "repository", repo_id, "/zabbix/zabbixAgentInstall.sh", "main", "resource")
create_file_template("zabbix/zabbix_agentd.conf", "provision", "Zabbix Agent File", "zabbix_agentd.conf", "/etc/zabbix", "root", "zabbixagent", "Agent")
zabbix_agent_file_template_id = get_file_template_id_name("Zabbix Agent File")
add_library_task("Zabbix Agent File", "zabbixAgentFile", zabbix_agent_file_template_id)
add_task("Zabbix Agent Restart", "zabbixAgentRestart", "1", "script", "on", "repository", repo_id, "/zabbix/zabbixAgentRestart.sh", "main", "resource")

## Add tasks for Zabbix Monitoring Workflow - Tested
add_task_remote("Zabbix Add IP", "zabbixAddIP", "1", "script", "on", "107.21.198.117", "22", "repository", repo_id, "/zabbix/zabbixAddIP.sh", "main", "remote", cred_id)
add_python_task("Zabbix Get API Token", "zabbixAPIToken", "22", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixGetAPIToken.py", "main", "<%= cypher.read('secret/zServerIP',true) %> <%= cypher.read('secret/zAPIPass',true) %>", "requests")
add_python_task("Zabbix Add Host", "zabbixAddHost", "22", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixAddHost.py", "main", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_python_task("Zabbix Release API", "zabbixRelAPI", "22", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixReleaseAPI.py", "main", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_python_task("Zabbix Get Host", "zabbixGetHost", "22", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixGetHost.py", "main", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_python_task("Zabbix Remove Host", "zabbixRemoveHost", "22", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixRemoveHost.py", "main", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_task_remote("Zabbix Remove IP", "zabbixRemoveIP", "1", "script", "on", "107.21.198.117", "22", "repository", repo_id, "/zabbix/zabbixRemoveIP.sh", "main", "remote", cred_id)
add_python_task("Zabbix Disable Host", "zabbixDisableHost", "22", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixDisableHost.py", "main", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_python_task("Zabbix Enable Host", "zabbixEnableHost", "22", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixEnableHost.py", "main", "<%= cypher.read('secret/zServerIP',true) %>", "requests")

##Postgres Standalone - Tested
create_cypher_secret("postgres", "0", "Password123?")
add_script_template("postgres install standalone", "bash", "provision", "PGPass=\"<%=cypher.read('secret/postgres')%>\"\n\n#Update all packages with available update\napt update -y\n\n#Install Postgres\nsh -c 'echo \"deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main\" > /etc/apt/sources.list.d/pgdg.list'\nwget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -\napt update -y\napt -y install postgresql-14 postgresql-server-dev-14\n\nsystemctl enable postgresql.service\nsystemctl stop postgresql.service\n\necho \"listen_addresses = '*'\" >> /etc/postgresql/14/main/postgresql.conf\necho \"host  all  all 0.0.0.0/0 md5\" >> /etc/postgresql/14/main/pg_hba.conf\n\nsystemctl start postgresql.service\n\nsudo -u postgres psql template1 -c \"CREATE USER admin WITH SUPERUSER PASSWORD '$PGPass';\"", "", "on")

##Postgres Cluster Script Templates for Ubuntu - Tested
add_script_template("etcd install", "bash", "preProvision", "#Update all packages with available update\napt update -y\n#Install etcd\ncd /home/morpheusci\nfile_url_etcd=\"<%= archives.link('Automation Training Archive', 'etcd-v3.5.19-linux-amd64.tar.gz', 1200) %>\"\nwget $file_url_etcd -O \"./etcd-v3.5.19-linux-amd64.tar.gz\" --no-check-certificate\ntar xzf /home/morpheusci/etcd-v3.5.19-linux-amd64.tar.gz\nmv /home/morpheusci/etcd-v3.5.19-linux-amd64/etcd* /usr/local/bin\n\nmkdir -p /var/lib/etcd/\nmkdir /etc/etcd\ngroupadd --system etcd\nuseradd -s /sbin/nologin --system -g etcd etcd\nchown -R etcd:etcd /var/lib/etcd/\nchmod -R a+rw /var/lib/etcd\n\ncat <<EOF | sudo tee /etc/systemd/system/etcd.service\n[Unit]\nDescription=etcd key-value store\nDocumentation=https://github.com/etcd-io/etcd\nAfter=network-online.target local-fs.target remote-fs.target time-sync.target\nWants=network-online.target local-fs.target remote-fs.target time-sync.target\n\n[Service]\nUser=etcd\nType=notify\nEnvironment=ETCD_DATA_DIR=/var/lib/etcd\nEnvironment=ETCD_NAME=%H\nEnvironmentFile=-/etc/etcd/etcd.conf\nExecStart=/usr/local/bin/etcd\nRestart=always\nRestartSec=10s\nLimitNOFILE=40000\n\n[Install]\nWantedBy=multi-user.target\nEOF", "", "on")
add_script_template("etcd setup", "bash", "provision", "#Copy the file template etcd.conf into place and set ownership and permissions\ncp /tmp/patroni/etcd /etc/etcd/etcd.conf\nchown root:root /etc/etcd/etcd.conf\nchmod 644 /etc/etcd/etcd.conf\n#Start etcd and enable on boot\nsystemctl daemon-reload\nsystemctl enable etcd.service\nsystemctl restart etcd.service", "", "on")
add_script_template("postgres install", "bash", "preProvision", "#Update all packages with available update\napt update -y\n\n#Install Postgres\napt-get install curl ca-certificates -y\ninstall -d /usr/share/postgresql-common/pgdg\ncurl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc\nsh -c 'echo \"deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main\" > /etc/apt/sources.list.d/pgdg.list'\napt-get update -y\napt -y install postgresql-17 postgresql-server-dev-17\nsystemctl stop postgresql && systemctl disable postgresql\n\nln -s /usr/lib/postgresql/17/bin/* /usr/sbin/\n\n#Install Patroni\napt-get -y install python3 python3-pip sshpass libpq-dev\n\npip install patroni==4.0.5 --break-system-packages\npip install psycopg --break-system-packages\npip install python-etcd --break-system-packages\n\n#Create post_bootstrap.sh script\nPGPass=\"<%=cypher.read('secret/postgres')%>\"\ncat <<EOF > /post_bootstrap.sh\n#!/bin/sh\npsql -U postgres -c \"CREATE USER admin WITH CREATEROLE CREATEDB PASSWORD '$PGPass';\"\nEOF\nchown postgres:postgres /post_bootstrap.sh\nchmod 700 /post_bootstrap.sh", "", "on")
add_script_template("postgres setup", "bash", "provision", "HOSTNAME=`hostname`\n#Copy the file template patroni.yml into place and set ownership and permissions\ncp /tmp/patroni/patroni.yml /etc/patroni.yml\nchown postgres:postgres /etc/patroni.yml\nchmod 600 /etc/patroni.yml\n\nmkdir -p /data/patroni\nchown postgres:postgres /data/patroni\nchmod 700 /data/patroni\n\nsed -i '/pg_cluster\\// a name:\\ '\"$HOSTNAME\"'' /etc/patroni.yml\n\n#Get the IP address of the postgres instances\nPOSTGRESIP=$(echo \"<%= instance.containers.findAll{it.containerTypeShortName == 'postgres'}.collect{it.internalIp}.join(',') %>\" | sed 's/,/ /')\nETCDIP=\"<%= instance.containers.findAll{it.containerTypeShortName == 'etcd'}.collect{it.internalIp}.join(',') %>\"\n\n#Add etcd instance IP to patroni.yml file\nsed -i 's/ETCDIP:2379/'\"$ETCDIP\"':2379/' /etc/patroni.yml\n\n#Remove comma from postgres instance IPs\n#POSTGRESIP=`cat /tmp/postgresip | sed 's/,/ /'`\n\n#Add postgres IPs to postgresql.yml file\nfor i in $(echo $POSTGRESIP)\ndo\n    sed -i '/127.0.0.1\\/32 md5/ a \\ \\ -\\ host\\ replication\\ replicator '\"$i\"'\\/0 md5' /etc/patroni.yml\ndone\n\ncat <<EOF > /etc/systemd/system/patroni.service\n[Unit]\nDescription=High availability PostgreSQL Cluster\nAfter=syslog.target network.target\n[Service]\nType=simple\nUser=postgres\nGroup=postgres\nExecStart=/usr/local/bin/patroni /etc/patroni.yml\nKillMode=process\nTimeoutSec=30\nRestart=no\n\n[Install]\nWantedBy=multi-user.target\nEOF\n\n#Start patroni and enable on boot\nsystemctl daemon-reload\nsystemctl enable patroni\n\nmodprobe softdog\nchown postgres /dev/watchdog\n\nsystemctl start patroni", "", "on")
add_script_template("haproxy install", "bash", "preProvision", "#Add PPA repository\nadd-apt-repository ppa:vbernat/haproxy-3.1 -y\n#Update all packages with available update\napt-get update -y\n#Install haproxy\napt-get install haproxy -y\n#Make a copy of original config file\nmv /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.orig", "", "on")
add_script_template("haproxy setup", "bash", "provision", "#Copy the file template haproxy.cfg into place and set ownership and permissions\n\ncp /tmp/patroni/haproxy.cfg /etc/haproxy \nchown root:root /etc/haproxy/haproxy.cfg\nchmod 644 /etc/haproxy/haproxy.cfg\n\n#Get the IPs of the postgres nodes\nips=\"<%= instance.containers.findAll{it.containerTypeShortName == 'postgres'}.collect{it.externalIp}.join(',') %>\"\nhostnames=\"<%= instance.containers.findAll{it.containerTypeShortName == 'postgres'}.collect{it.server.name}.join(',') %>\"\nip1=`echo $ips| awk -F ',' {'print $1'}`\nip2=`echo $ips| awk -F ',' {'print $2'}`\nhostname1=`echo $hostnames| awk -F ',' {'print $1'}`\nhostname2=`echo $hostnames| awk -F ',' {'print $2'}`\n\n#Configure the haproxy.cfg file to load balance postgres\nsed -i '/sessions/ a \\ \\ \\ \\ server '\"$hostname1\"' '\"$ip1\"':5432 maxconn 100 check port 8008' /etc/haproxy/haproxy.cfg\nsed -i '/sessions/ a \\ \\ \\ \\ server '\"$hostname2\"' '\"$ip2\"':5432 maxconn 100 check port 8008' /etc/haproxy/haproxy.cfg\n\n#Start haproxy and enable on boot\nsystemctl enable haproxy\nsystemctl restart haproxy", "", "on")

##Postgres Cluster File Templates for Ubuntu - Tested
create_file_template("postgres/etcd", "preProvision", "Etcd Configuration File", "etcd", "/tmp/patroni", "root", "etcdconf", "App")
create_file_template("postgres/patroni.yml", "preProvision", "Patroni Configuration File", "patroni.yml", "/tmp/patroni", "root", "patroniconf", "DB")
create_file_template("postgres/haproxy.cfg", "preProvision", "Haproxy Configuration File", "haproxy.cfg", "/tmp/patroni", "root", "haproxyconf", "App")

##Postgres Tasks
add_python_task("Postgres Set Evar", "postgresSetEvar", "22", "jythonTask", "", "repository", repo_id, "/postgres/postgresSetEvar.py", "main", "", "requests")

## Add tasks for ToDo application
add_task("ToDo Setup", "todosetup", "1", "script", "on", "repository", repo_id, "/todo/todoSetup.sh", "main", "resource")
add_task("ToDo Deployment Setup", "tododeploysetup", "1", "script", "on", "repository", repo_id, "/todo/todoDeploySetup.sh", "main", "resource")

## ToDo Script Templates
add_script_template("todo start service", "bash", "start", "systemctl start todo", "", "on")
add_script_template("todo stop service", "bash", "stop", "systemctl stop todo", "", "on")

## Add tasks for Update Wiki
add_python_task("Update Wiki", "updateWiki", "22", "jythonTask", "value", "repository", repo_id, "updateWiki.py", "main", "", "requests")

## JSON Server
create_file_template("option_lists/app.json", "provision", "App JSON", "app.json", "/opt/jsonserver", "root", "appjson", "App")
app_json_template_id = get_file_template_id_name("App JSON")
task_id1 = add_task("JSON Server Install", "jsonServerInstall", "1", "script", "on", "repository", repo_id, "/option_lists/json_server_install.sh", "main", "resource")
task_id2 = add_task("JSON Server Start", "jsonServerStart", "1", "script", "on", "repository", repo_id, "/option_lists/json_server_start.sh", "main", "resource")
task_id3 = add_task("JSON Server Stop", "jsonServerStop", "1", "script", "on", "repository", repo_id, "/option_lists/json_server_stop.sh", "main", "resource")
add_workflow("JSON Server Install", task_id1, "provision", task_id2, "start", task_id3, "stop")