import base64
import hashlib
import hmac
import json
import os
import socket
import sys
import time
from functools import wraps

import bittensor.btlogging as log
import requests
import bittensor as bt
from dotenv import load_dotenv
from flask import Response, render_template
from flask import request
from flask_openapi3 import Info, Server
from flask_openapi3 import OpenAPI

from model import InputNetuid, KeyAddress, UidAddress

load_dotenv("bittensor_http_api/.env")


def get_env(env_name):
    if not os.getenv(env_name):
        sys.exit("Missing env $%s" % env_name)
    return os.getenv(env_name)


info = Info(title="Bittensor HTTP API", version="1.0.0")

log.logging.info("Hostname: " + socket.gethostname())

SUBTENSOR_NETWORK = get_env("SUBTENSOR_NETWORK")

KUCOIN_API_KEY = get_env("KUCOIN_API_KEY")
KUCOIN_API_SECRET = get_env("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = get_env("KUCOIN_API_PASSPHRASE")
KUCOIN_API_ENDPOINT = get_env("KUCOIN_API_ENDPOINT")

WALLETS = {
    "senrie": "5C5zpdLSSxFeFkLFw9tAc7DdxdK82GCAjnoe5pub73GMvKLt",
    "senrie2": "5GHWtT4nzUi8S7exH1aGsjq8gbJRxZyoibtPwyzmyq9skiE3",
    "senrie3": "5F1rDyF5xmTGcAwHo4C7XnjYJghJQoapaUB2R4V4gJNXZTYG",
    "senrie4": "5Gy1fhT3XbULENG2vHpbxE77Doqhn9s7ADNq7VuXQ3sMyTh1",
    "senrie6": "5DRmsiaXjYqzZqXznD56uDrA8fcz6MVex8PRzMFtcKJ82P97",
    "senrie7": "5ELVUt1AXodQSMhedPM9iMh4Uj2WEsFZSabYzHzdi4kkqiRf",
    "senrie8": "5Fj8di9ew5VDUnWnjw4BzY1ZmLmJDiStMMiu8cGj8X53puo1",
    "senrie9": "5EnD6mJspqmK1ykHQbXLKKsKbRHDN8HXsfmg3vj5JDDN8pnw",
    "senrie10": "5Fgb2eYvPkRm3994atNfNaaHLNiGhpwp1YbHWEpM3pDRpYKn",

    "senrie11": "5G74QUD44W2iVxtJCki74NbmF7EDAKs61v3ebQfaYAziAy92",
    "senrie12": "5EeKLUA3C9ib4xBubbi4KAbKnsQ8Du53UpaLrBZHDYt3w3Zv",
    "senrie13": "5EPTvbXRqbZtcYf8mid83cU6LRJwdTJnWDfdVdfvTiPpd6tM",
    "senrie14": "5Fgb2eYvPkRm3994atNfNaaHLNiGhpwp1YbHWEpM3pDRpYKn",
    "senrie15": "5CB2eYwA1Ki9beRHXqe4nXZQjuW9ed1f3e3bbbnxFcUkojWy",
    "senrie16": "5FTWBFFPSrJUoKC7YtcNHWPUPTiLD55UktiYEvHCpeJuHhC8",
    "senrie17": "5HiWTBbLH3Thgo1mvmmWoVdWbWv8ZAvNv7fHpSAaUJEZjjPg",
    "senrie18": "5GGxpfLT74kHQ1n8XrLCbM8bQgaDhgQuig8C2FyxW1yJZhTQ",
    "senrie19": "5HT4D8jx8a8htH1VThKgEGruJoo44jFiv2SXB33X61hVjK4v",
    "senrie20": "5CDUADbgqMKBo45X6sn1swpfXzeb71ry2QMwuvmzpPGHXHvr",

    "quocbao": "5EsxvyJA25MqhAu2jBAMtPM53G5rQzoQb1BSSVAbA69M3wrA",
    "quocbao2": "5DEyfuDjgZ1Ujj2uHhBwQuMz1x92WA2WeU1FzqroJinF8SKe",

    "wstorage": "5FNmZE2PEJSucSchWK6ugr2fnv5vtAa6xsvjS2TKJZUa2WAj",
}


def create_app():
    """
    Create and initialize our app. Does not call its run() method
    """

    # flask_app = Flask(__name__)
    flask_app = OpenAPI(
        __name__,
        info=info, servers=[
            Server(url="http://localhost:8080"),
        ]
    )

    return flask_app


bittensor_http_api = create_app()


@bittensor_http_api.get('/api/v1/subnets', summary="Get all subnets info", tags=[])
# def get_subnets(netuid: str):
def get_subnets():
    subnets = []
    for subnet in bt.subtensor(network=SUBTENSOR_NETWORK).get_all_subnets_info():
        subnets.append({
            "netuid": subnet.netuid,
            "immunity_period_block": subnet.immunity_period,
            "immunity_period_hours": round(subnet.immunity_period * 12 / 3600, 2),
            "subnetwork_n": subnet.subnetwork_n,
            "max_n": subnet.max_n,
            "emission_value": round(subnet.emission_value / 10_000_000, 2),
            "burn": round(subnet.burn.tao, 5),
            "owner_ss58": subnet.owner_ss58
        })

    if request.args.get("output") == "html":
        return render_template('index.html', data=subnets)

    return Response(
        json.dumps({
            "subnets": subnets,
        }),
        status=200,
        mimetype='application/json'
    )


@bittensor_http_api.get('/api/v1/netuid/<int:netuid>', summary="Get all subnets info", tags=[])
def get_subnet(path: InputNetuid):
    subnet_metagraph = bt.subtensor(network=SUBTENSOR_NETWORK).metagraph(path.netuid)

    uids = []
    for neuron in subnet_metagraph.neurons:
        uids.append({
            "uid": neuron.uid,
            "coldkey": neuron.coldkey,
            "hotkey": neuron.hotkey,
            "emission": round(neuron.emission, 6),
            "incentive": round(neuron.incentive, 6),
            "total_stake": round(neuron.total_stake.tao, 5),
            "trust": round(neuron.trust, 6),
            "validator_trust": round(neuron.validator_trust, 5),
            "validator_permit": neuron.validator_permit,

        })

    return Response(
        json.dumps({
            "block": int(subnet_metagraph.block),
            "time_epoch": int(time.time()),
            "netuid": path.netuid,
            "uids": uids,
        }),
        status=200,
        mimetype='application/json'
    )

@bittensor_http_api.get('/api/v1/netuid/<int:netuid>/uid/<int:uid>', summary="Get subnet uid status", tags=[])
def get_uid_info(path: UidAddress):
    time_start = time.time()

    if request.args.get('check_immunity'):
        st = bt.subtensor(network="archive")
    else:
        st = bt.subtensor(network=SUBTENSOR_NETWORK)

    current_block = st.get_current_block()
    bt.logging.info(f"Current block: {current_block}")

    subnet_metagraph = st.metagraph(path.netuid)
    uid_info = subnet_metagraph.neurons[path.uid]
    #subnet_info = st.get_subnet_info(netuid=path.netuid)

    uid_hotkey = uid_info.hotkey

    # Currently lite node only store information of 300-most recent block
    subnet_immunity_period = st.get_subnet_info(path.netuid).immunity_period
    bt.logging.info(f"Subnet {path.netuid} as immunity period = {subnet_immunity_period}")

    response = {
        "block": current_block,
        "time_epoch": int(time.time()),
        "run_time_seconds": f"{round(time.time() - time_start, 2)}",
        "data": {
            "uid": path.uid,
            "netuid": path.netuid,
            "immunity_period": subnet_immunity_period,
            "coldkey": uid_info.coldkey,
            "hotkey": uid_info.hotkey,
            "incentive": round(uid_info.incentive, 6),
    #        "daily_rewards_tao": round(uid_info.incentive, 6),
            "emission": round(uid_info.emission, 6),
            "axon": f"{uid_info.axon_info.ip}:{uid_info.axon_info.port}",
            "axon_serving": uid_info.axon_info.is_serving,
        }
    }

    if request.args.get('check_immunity'):
        uid_hotkey_last_period = st.metagraph(netuid=path.netuid, block=current_block - subnet_immunity_period).neurons[
            path.uid].hotkey
        response["data"]["is_in_immunity_period"] = uid_hotkey != uid_hotkey_last_period

    return Response(
        json.dumps(response),
        status=200,
        mimetype='application/json'
    )


@bittensor_http_api.get('/api/v1/cold_key/<string:ss58_address>', summary="Get cold key stake", tags=[])
def get_coldkey_stake(path: KeyAddress):
    time_start = time.time()
    st = bt.subtensor(network=SUBTENSOR_NETWORK)
    cold_key = path.ss58_address

    try:
        if st.does_hotkey_exist(path.ss58_address):
            return Response(
                json.dumps({
                    "error": "Input address is not a cold key. Cold key required"
                }),
                status=400,
                mimetype='application/json'
            )
    except Exception as e:
        return Response(
            json.dumps({
                "error": str(e)
            }),
            status=400,
            mimetype='application/json'
        )

    cold_key_stake = st.get_stake_info_for_coldkey(cold_key)
    if cold_key_stake is None:
        # log.logging.warning(f"Cold key {cold_key} does not have any hot key on the network")
        return Response(
            json.dumps({
                "block": int(st.block),
                "time_epoch": int(time.time()),
                "run_time_seconds": f"{round(time.time() - time_start, 2)}",
                "error": f"Cold key {cold_key} does not have any hot key on the network"
            }),
            status=400,
            mimetype='application/json'
        )

    stake_coldkey = []
    total_hotkey = 0
    for stake in cold_key_stake:
        if stake.stake.rao == 0:
            continue

        stake_coldkey.append({
            "hot_key": stake.hotkey_ss58,
            "tao": round(stake.stake.tao, 5),
        })
        total_hotkey += stake.stake.tao

    balance = st.get_balance(cold_key)

    return Response(
        json.dumps({
            "block": int(st.block),
            "time_epoch": int(time.time()),
            "run_time_seconds": f"{round(time.time() - time_start, 2)}",
            "data": {
                "cold_key": cold_key,
                "stake": stake_coldkey,
                "total": {
                    "hot_key": round(total_hotkey, 5),
                    "cold_key": round(balance.tao, 5),
                    "total": round(total_hotkey + balance.tao, 5)
                }
            }
        }),
        status=200,
        mimetype='application/json'
    )


def check_auth(username, password):
    return username == 'bao' and password == 'bao'


def login_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        if not (auth and check_auth(auth.username, auth.password)):
            return ('Unauthorized', 401, {
                'WWW-Authenticate': 'Basic realm="Login Required"'
            })

        return f(**kwargs)

    return wrapped_view

@bittensor_http_api.get('/api/v1/total', summary="Get cold key stake", tags=[])
@login_required
def get_total_tao():
    start_time = time.time()
    subtensor_call = 0
    block_shift = 0

    st = bt.subtensor(network=SUBTENSOR_NETWORK)

    try:
        current_block = st.get_current_block()
        subtensor_call += 1
    except Exception as e:
        log.logging.error(e)
        log.logging.error(f"Error when using subtensor endpoint {SUBTENSOR_NETWORK}, switching to finney ...")
        st = bt.subtensor(network="finney")
        current_block = st.get_current_block()
        subtensor_call += 1

    total_tao_hot_keys = 0
    total_tao_cold_keys = 0
    wallets_return = {}

    for wallet_name in WALLETS.keys():
        cold_key = WALLETS[wallet_name]

        wallets_return[wallet_name] = {
            "cold_key": cold_key,
            "hot_key": {}
        }

        subtensor_call += 1
        cold_key_stake = st.get_stake_info_for_coldkey(cold_key, block=current_block - block_shift)
        if cold_key_stake is None:
            log.logging.warning(f"Cold key {cold_key} ({wallet_name}) does not have any hot key on the network")
            cold_key_stake = {}

        hot_key_balance = 0
        for stake_info in cold_key_stake:

            if stake_info.stake.tao == 0:
                continue

            wallets_return[wallet_name]["hot_key"][stake_info.hotkey_ss58] = round(stake_info.stake.tao, 4)
            hot_key_balance += stake_info.stake.tao
            total_tao_hot_keys += stake_info.stake.tao

            log.logging.info(f"wallet {wallet_name} -> hot key {stake_info.hotkey_ss58} -> {stake_info.stake.tao} tao")

        cold_key_balance = st.get_balance(cold_key, block=current_block - block_shift).tao
        log.logging.info(f"wallet {wallet_name} -> cold key balance -> {cold_key_balance} tao")
        subtensor_call += 1
        total_tao_cold_keys += cold_key_balance

        wallets_return[wallet_name]["cold_key_balance"] = round(cold_key_balance, 4)
        wallets_return[wallet_name]["wallet_balance"] = round(cold_key_balance + hot_key_balance, 4)

    kucoin_account, kucoin_tao = kucoin_account_info()

    tao_price_usd = kucoin_tao_price_usd()
    tao_price_vnd = kucoin_tao_price_vnd()

    total_tao_wallets = total_tao_hot_keys + total_tao_cold_keys
    total_tao = kucoin_tao + total_tao_wallets

    response_data = {
        "block": current_block,
        "time_epoch": int(time.time()),
        "wallets": wallets_return,
        "kucoin": kucoin_account,
        "price": {
            "tao_price_usd": round(tao_price_usd, 2),
            "tao_price_vnd": round(tao_price_vnd),
        },
        "total": {
            "total_tao_hot_keys": round(total_tao_hot_keys, 4),
            "total_tao_cold_keys": round(total_tao_cold_keys, 4),
            "total_tao_wallets": round(total_tao_wallets, 4),
            "total_tao_kucoin": round(kucoin_tao, 4),
            "total_tao": round(total_tao, 4),
            "total_tao_usd": round(total_tao * tao_price_usd, 2),
            "total_tao_usd_str": f"{total_tao * tao_price_usd:9,.2f} USD",
            "total_tao_vnd": round(total_tao * tao_price_vnd),
            "total_tao_vnd_str": f"{total_tao * tao_price_vnd:11,.0f} VND",
        }
    }

    return Response(
        json.dumps({
            "block": current_block,
            "time_epoch": int(time.time()),
            "run_time_seconds": f"{round(time.time() - start_time, 2)}",
            "subtensor_call": subtensor_call,
            "data": response_data
        }),
        status=200,
        mimetype='application/json'
    )


def kucoin_sign(str_to_sign):
    return base64.b64encode(
        hmac
        .new(
            KUCOIN_API_SECRET.encode('utf-8'),
            str_to_sign.encode('utf-8'),
            hashlib.sha256
        )
        .digest()
    )


def kucoin_api_get(method, url):
    now = int(time.time() * 1000)
    str_to_sign = f"{str(now)}{method}{url}"
    signature = kucoin_sign(str_to_sign)
    passphrase = kucoin_sign(KUCOIN_API_PASSPHRASE)
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": KUCOIN_API_KEY,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2"
    }
    response = requests.request('get', f"{KUCOIN_API_ENDPOINT}{url}", headers=headers)

    return response.json()


def kucoin_tao_price_usd():
    return float(kucoin_api_get("GET", "/api/v1/prices?base=USD&currencies=TAO")["data"]["TAO"])


def kucoin_tao_price_vnd():
    return float(kucoin_api_get("GET", "/api/v1/prices?base=VND&currencies=TAO")["data"]["TAO"])


def kucoin_account_info():
    account_info = kucoin_api_get("GET", "/api/v1/accounts")["data"]

    total_tao = 0

    ''' 
        Written by ChatGPT
    '''
    result = {}
    for item in account_info:

        if item["currency"] not in ["TAO", "USDT", "MATIC"] or float(item["balance"]) == 0:
            continue

        if item["currency"] in result:
            if item["type"] == "trade":
                result[item["currency"]]["trade_account"] = round(float(item["balance"]), 4)
            elif item["type"] == "main":
                result[item["currency"]]["funding_account"] = round(float(item["balance"]), 4)
        else:
            result[item["currency"]] = {}
            if item["type"] == "trade":
                result[item["currency"]]["trade_account"] = round(float(item["balance"]), 4)
            elif item["type"] == "main":
                result[item["currency"]]["funding_account"] = round(float(item["balance"]), 4)

        if item["currency"] == "TAO":
            total_tao += float(item["balance"])

    return result, total_tao


if __name__ == '__main__':
    bittensor_http_api.run(host='0.0.0.0', port=8080, debug=False)
