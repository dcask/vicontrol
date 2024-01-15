from fastapi import FastAPI
from pymongo import MongoClient, errors
from routers import mongo_router, shell_router
from urllib.parse import quote_plus
import paramiko

import os

mongouser=''
mongopassword=''

with open('/run/secrets/MONGO_AUTH_USER', 'r') as f:
    mongouser=f.read().rstrip()
with open('/run/secrets/MONGO_AUTH_PASSWORD', 'r') as f:
    mongopassword=f.read().rstrip()
with open('/run/secrets/SSH_AUTH_USER', 'r') as f:
    ssh_user=f.read().rstrip()
#with open('/run/secrets/SSH_AUTH_PASSWORD', 'r') as f:
#    ssh_password=f.read().rstrip()

ostream = os.popen("/sbin/ip route|awk '/default/ { print $3 }'")
SSH_HOST = ostream.read().rstrip()
ostream.close()

print("ssh host", SSH_HOST, '---')

DB_NAME = os.getenv('MONGODB_NAME')
MONGO_HOST_NAME = os.getenv('MONGODB_HOST')
HOST = os.getenv('PLATFORM_URL')
mongo_uri = "mongodb://%s:%s@%s/%s?directConnection=true" % (quote_plus(mongouser), quote_plus(mongopassword), MONGO_HOST_NAME, DB_NAME)

app = FastAPI(docs_url=None, redoc_url="/control/docs",openapi_url="/control/openapi.json" )

app.include_router(mongo_router, prefix="/control")
app.include_router(shell_router, prefix="/control")

@app.on_event("startup")
def startup_db_client():
    #host='localhost', port=27017, document_class=dict, tz_aware=False, connect=True, **kwargs
    #print('mongo connect', mongo_uri, 'db', DB_NAME)
    try:
        app.mongodb_client = MongoClient(mongo_uri)
        app.collections = app.mongodb_client[DB_NAME]
        app.host = HOST
        app.mongodb_client.server_info()
    except errors.ServerSelectionTimeoutError as err:
        print(err)
    app.ssh_client = paramiko.SSHClient()
    app.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #app.ssh_client.connect(hostname=SSH_HOST, username=ssh_user, password=ssh_password,key_filename='/run/secrets/SSH_AUTH_KEY')
    app.ssh_client.connect(hostname=SSH_HOST, username=ssh_user, key_filename='/run/secrets/SSH_AUTH_KEY')
    #ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
    app.ssh_client.close()
