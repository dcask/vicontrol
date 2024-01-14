from fastapi import APIRouter, Depends, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from validator import validate_visiology
#from fastapi.responses import JSONResponse
#from fastapi.encoders import jsonable_encoder
from typing import List
import json

mongo_router = APIRouter(
    prefix="/mongo",
    tags=["admin"],
    dependencies=[Depends(validate_visiology)],
    responses={404: {"description": "Not found"}}
)
@mongo_router.get("/{name}", response_description="Get item list of a collection by name", response_model=List)
async def get_collection(name: str, request: Request):
    collection = [ str(i) for i in request.app.collections[name].find(limit=100)]
    
    
    return collection

shell_router = APIRouter(
    prefix="/shell",
    tags=["admin"],
    dependencies=[Depends(validate_visiology)],
    responses={404: {"description": "Not found"}}
)


@shell_router.get("/restart", response_description="Restart platform")
async def restart_platfrom(request: Request):
    #cmd_to_execute = '/var/lib/visiology/scripts/run.sh --restart'
    cmd_to_execute = 'docker service ls'
    ssh_stdin, ssh_stdout, ssh_stderr = request.app.ssh_client.exec_command(cmd_to_execute)
    output = ssh_stdout.readlines()
    errors = ssh_stderr.readlines()
    return {'stdout':output, 'stderr':errors}