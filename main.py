import requests
import time
import hmac
import hashlib
import logging
from threading import Lock
from keys import *
from okx.websocket.WsPublicAsync import WsPublicAsync

# OKX API密钥和秘密
api_key = API_KEY
api_secret = SECRET
api_passphrase = PASS_PHRASE

# OKX API URL
public_url = "wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999"

# 生成签名
def generate_signature(timestamp, method, request_path, body):
    message = timestamp + method + request_path + body
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

# 获取当前时间戳
def get_timestamp():
    return str(int(time.time() * 1000))

# 获取账户余额
def get_balance():
    timestamp = get_timestamp()
    method = 'GET'
    request_path = '/api/v5/account/balance'
    body = ''
    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': generate_signature(timestamp, method, request_path, body),
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': api_passphrase,
        'Content-Type': 'application/json'
    }
    response = requests.get(base_url + request_path, headers=headers)
    return response.json()

# 下单
def place_order(inst_id, side, size, price):
    timestamp = get_timestamp()
    method = 'POST'
    request_path = '/api/v5/trade/order'
    body = {
        'instId': inst_id,
        'side': side,
        'ordType': 'limit',
        'sz': size,
        'px': price
    }
    body = json.dumps(body)
    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': generate_signature(timestamp, method, request_path, body),
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': api_passphrase,
        'Content-Type': 'application/json'
    }
    response = requests.post(base_url + request_path, headers=headers, data=body)
    return response.json()

# 示例：获取账户余额
balance = get_balance()
print(balance)

# 示例：下单
order = place_order('BTC-USDT', 'buy', '0.01', '30000')
print(order)
import websocket
import json
import hmac
import hashlib
import time

# OKX API密钥和秘密
api_key = '你的API密钥'
api_secret = '你的API秘密'
api_passphrase = '你的API密码'

# WebSocket消息处理
def on_message(ws, message):
    data = json.loads(message)
    print(data)

# WebSocket错误处理
def on_error(ws, error):
    print(error)

# WebSocket关闭处理
def on_close(ws):
    print("WebSocket closed")

# WebSocket打开处理
def on_open(ws):
    print("WebSocket connected")
    # 订阅BTC-USDT和BTC-USDT-SWAP的市场数据
    subscribe_message = {
        "op": "subscribe",
        "args": [
            {"channel": "tickers", "instId": "BTC-USDT"},
            {"channel": "tickers", "instId": "BTC-USDT-SWAP"}
        ]
    }
    ws.send(json.dumps(subscribe_message))

# 启动WebSocket连接
ws = websocket.WebSocketApp(ws_url,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
ws.run_forever()

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OKX API密钥和秘密
api_key = '你的API密钥'
api_secret = '你的API秘密'
api_passphrase = '你的API密码'

# Redis配置
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# WebSocket URL
ws_url = 'wss://ws.okx.com:8443/ws/v5/public'

# 生成签名
def generate_signature(timestamp, method, request_path, body):
    message = timestamp + method + request_path + body
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

# 获取当前时间戳
def get_timestamp():
    return str(int(time.time() * 1000))

# 下单函数
async def place_order(inst_id, side, size, price):
    timestamp = get_timestamp()
    method = 'POST'
    request_path = '/api/v5/trade/order'
    body = json.dumps({
        'instId': inst_id,
        'side': side,
        'ordType': 'limit',
        'sz': size,
        'px': price
    })
    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': generate_signature(timestamp, method, request_path, body),
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': api_passphrase,
        'Content-Type': 'application/json'
    }
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(json.dumps(headers))
        response = await websocket.recv()
        logger.info(f"Order response: {response}")

# 处理WebSocket消息
async def on_message(message):
    data = json.loads(message)
    if 'data' in data:
        spot_price = float(data['data'][0]['last'])
        swap_price = float(data['data'][1]['last'])
        redis_client.set('spot_price', spot_price)
        redis_client.set('swap_price', swap_price)
        logger.info(f"Spot Price: {spot_price}, Swap Price: {swap_price}")

        # 交易逻辑
        if swap_price > spot_price * 1.003:
            await place_order('BTC-USDT-SWAP', 'sell', '0.01', swap_price)
        elif spot_price > swap_price * 1.003:
            await place_order('BTC-USDT-SWAP', 'buy', '0.01', spot_price)
        elif abs(swap_price - spot_price) <= spot_price * 0.0005:
            await place_order('BTC-USDT-SWAP', 'close', '0.01', spot_price)

# WebSocket连接
async def connect():
    async with websockets.connect(ws_url) as websocket:
        subscribe_message = {
            "op": "subscribe",
            "args": [
                {"channel": "tickers", "instId": "BTC-USDT"},
                {"channel": "tickers", "instId": "BTC-USDT-SWAP"}
            ]
        }
        await websocket.send(json.dumps(subscribe_message))
        while True:
            message = await websocket.recv()
            await on_message(message)

# 主函数
if __name__ == "__main__":
    lock = Lock()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect())

