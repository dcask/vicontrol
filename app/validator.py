from fastapi import Request
import requests
from fastapi import HTTPException
import jwt
import json

CERTS_URL = "/idsrv/.well-known/openid-configuration/jwks"

async def validate_visiology(request: Request):
    if verify_token(request) != True:
        raise HTTPException(status_code=403, detail="Authorizatuon failed")


def _get_public_keys(baseurl):
    public_keys = []
    try:
        print(baseurl+CERTS_URL)
        r = requests.get(baseurl+CERTS_URL)
        jwk_set = r.json()
        for key_dict in jwk_set["keys"]:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
            public_keys.append(public_key)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="openid configuration missing")
    return public_keys


def verify_token(request):
    token=''
    if "Authorization" in request.headers:
        token = request.headers["Authorization"].replace('Bearer ','')
    else:
        raise HTTPException(status_code=400, detail="missing required authorization token")

    keys = _get_public_keys(request.app.host)

    valid_token = False
    for key in keys:
        try:
            jwtdecoded=jwt.decode(token, key=key, algorithms=["RS256"], options={"verify_aud": False, "verify_signature": True})
            if 'Администратор' in jwtdecoded['role'] or 'vicontrol_role' in jwtdecoded['role']:
                valid_token = True
            break
        except Exception as e:
            print(str(e))
            raise HTTPException(status_code=400, detail="Error decoding token")
    if not valid_token:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    return True

def getTokenUser(token, keys):
    user = ''
    for key in keys:
        try:
            jwtdecoded=jwt.decode(token, key=key, algorithms=["RS256"], options={"verify_aud": False, "verify_signature": True})
            user = jwtdecoded['name']
        except Exception as e:
            pass
    return user
