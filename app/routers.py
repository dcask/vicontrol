from fastapi import APIRouter, Depends, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from validator import validate_visiology
#from fastapi.responses import JSONResponse
#from fastapi.encoders import jsonable_encoder
from typing import List
#from typing import Union
from bson.json_util import dumps
import json
main_router = APIRouter(
    tags=["admin"],
    #dependencies=[Depends(validate_visiology)],
    responses={404: {"description": "Not found at main"}}
)
@main_router.get("/status", response_description="It's alive!")
async def get_stat(request: Request):
    
    return {'details':'alive'}

mongo_router = APIRouter(
    prefix="/mongo",
    tags=["admin"],
    dependencies=[Depends(validate_visiology)],
    responses={404: {"description": "Not found at mongo"}}
)
@mongo_router.get("/{name}", response_description="Get item list of a collection by name", response_model=List)
async def get_collection(name: str, request: Request):
    #collection = [ json.loads(str(i).replace("\'", "\"")) for i in request.app.collections[name].find(limit=100)]
    collection = [ json.loads(dumps(i)) for i in request.app.collections[name].find(limit=100)]  
    
    return collection

shell_router = APIRouter(
    prefix="/shell",
    tags=["admin"],
    dependencies=[Depends(validate_visiology)],
    responses={404: {"description": "Not found at shell"}}
)


@shell_router.post("/restart", response_description="Restart platform")
async def restart_platfrom(request: Request):
    cmd_to_execute = 'nohup /var/lib/visiology/scripts/run.sh --restart > /dev/null &'
    ssh_stdin, ssh_stdout, ssh_stderr = request.app.ssh_client.exec_command(cmd_to_execute)
    output = ssh_stdout.readlines()
    errors = ssh_stderr.readlines()
    return {'detail':'done'}

@shell_router.post("/restart/{name}", response_description="Restart platform service 'name'")
async def restart_service(name:str, request: Request):
    cmd_to_execute = f'docker service update {name} --force'
    #print(cmd_to_execute)
    ssh_stdin, ssh_stdout, ssh_stderr = request.app.ssh_client.exec_command(cmd_to_execute)
    output = ssh_stdout.readlines()
    errors = ssh_stderr.readlines()
    return {'details':output,'errors':errors}

@shell_router.post("/log/{name}", response_description="Last N lines of service 'name' stdout")
async def log_service(name:str, request: Request, data=Body()):
    lines=100
    if 'lines' in data:
        lines=data['lines']
    cmd_to_execute = 'docker logs $(docker ps -a --format {{.ID}} --filter "name='+name+'" -l | awk \'{print $1}\') -n '+str(lines)
    #print(cmd_to_execute)
    ssh_stdin, ssh_stdout, ssh_stderr = request.app.ssh_client.exec_command(cmd_to_execute)
    output = ssh_stdout.readlines()
    errors = ssh_stderr.readlines()
    return {'details':output,'errors':errors}

@shell_router.post("/message", response_description="Send private or broadcast message")
async def broadcast_admin_message( request: Request, data = Body()):
    message=data['message']
    target=data['target']
    #print("request client host", request.client.host)
    #print("request client header", request.headers)
    if target == 'all':
	await request.app.manager.broadcast('{"command":"message","text":"'+message+'"}')
    else:
        request.app.manager.private_message('{"command":"message","text":"'+message+'"}', target)
    return {'details':'done'}

@shell_router.get("/connections", response_description="List of websocket connections", response_model=List)
async def service_list(request: Request):
    output = request.app.manager.connection_list()
    return output

@shell_router.get("/services", response_description="List of services", response_model=List)
async def service_list(request: Request):
    cmd_to_execute = f'docker service ls --format json | grep visiology2'
    ssh_stdin, ssh_stdout, ssh_stderr = request.app.ssh_client.exec_command(cmd_to_execute)
    output = [json.loads(line) for line in iter(ssh_stdout.readline, '')]
    #output = ssh_stdout.readline()
    #errors = ssh_stderr.readlines()
    #return {'details':ssh_stdout,'errors':ssh_stderr}
    return output