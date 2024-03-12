import ipaddress
import logging
import time, sys, os
from dotenv import load_dotenv
from functools import wraps
from flask import request
from flask_openapi3 import Info, Tag, Server
from flask_openapi3 import OpenAPI
import flask
import json
import socket
from flask import g
from flask import Response
import hashlib
import json 
from bittensor import subtensor, metagraph

load_dotenv(".env")

logging.basicConfig(filename="/dev/stdout",
    filemode='a',
    format='[%(asctime)s,%(msecs)d] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

def get_env(env_name):
    if not os.getenv(env_name):
        sys.exit("Missing env $%s" % env_name)
    return os.getenv(env_name)


info = Info(title="Bittensor HTTP API", version="1.0.0")

logging.info("Hostname: " + socket.gethostname())
APP_NAME=get_env("APP_NAME")
SUBTENSOR_NETWORK=get_env("SUBTENSOR_NETWORK")

def create_app():
    """
    Create and initialize our app. Does not call its run() method
    """

    #flask_app = Flask(__name__)
    flask_app = OpenAPI(
        __name__,
        info=info, servers=[
            Server(url="http://localhost:8080"),
        ]
    )

    return flask_app

btapi = create_app()

#@btapi.get('/api/v1/subnet/<integer:netuid>', summary="Get subnet info", tags=[])
@btapi.get('/api/v1/subnets', summary="Get all subnets info", tags=[])
def get_subnets(netuid: str):
    subtensor = subtensor(network=SUBTENSOR_NETWORK)
    return Response(
        subtensor.get_all_subnets_info(),
        status=200,
        mimetype='application/json'
    )

if __name__ == '__main__':
    btapi.run(host='0.0.0.0', port=8080, debug=False)
