import time
import redis
import threading
import websocket
import json
import ssl

# Configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
OKX_WS_URL = "wss://ws.okx.com:8443/ws/v5/public"
BTC_SPOT_SYMBOL = "BTC-USDT"
BTC_SWAP_SYMBOL = "BTC-USD-SWAP"
HEDGE_THRESHOLD = 0.003
CLOSE_THRESHOLD = 0.0005
TRADE_SIZE = 0.01  # Example Size
LOCK = threading.Lock()
# Redis setup
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# WebSocket instance
ws = None

# Function to calculate the price difference percentage
def calculate_price_difference(spot_price, swap_price):
    difference = (swap_price - spot_price) / spot_price
    return difference

# Function to place an order (placeholder)
def place_order(side, size):
    # Implement your order placing logic here using OKX API
    print(f"Placing {side} order for {size} contracts.")

# Function to process incoming websocket data
def on_message(ws, message):
    try:
        data = json.loads(message)
        if 'data' in data:
            for item in data['data']:
              if item['instId'] == BTC_SPOT_SYMBOL:
                spot_price = float(item['last'])
                redis_client.set("spot_price", spot_price)
              if item['instId'] == BTC_SWAP_SYMBOL:
                swap_price = float(item['last'])
                redis_client.set("swap_price", swap_price)

                with LOCK:
                  spot_price = redis_client.get("spot_price")
                  if spot_price:
                    spot_price = float(spot_price)
                    price_difference = calculate_price_difference(spot_price, swap_price)
                    position_open = redis_client.get("position_open")

                    if not position_open and price_difference > HEDGE_THRESHOLD:
                      print(f"Price diff {price_difference:.4f} is above threshold {HEDGE_THRESHOLD:.4f} - Opening Position")
                      place_order('long', TRADE_SIZE)
                      redis_client.set("position_open", "true")
                      redis_client.set("last_trade_price", swap_price)
                    elif position_open and price_difference < CLOSE_THRESHOLD:
                      print(f"Price diff {price_difference:.4f} is below close threshold {CLOSE_THRESHOLD:.4f} - Closing Position")
                      place_order('short', TRADE_SIZE)
                      redis_client.set("position_open", "false")

    except Exception as e:
        print(f"Error processing websocket message: {e}")

# WebSocket error handler
def on_error(ws, error):
    print(f"WebSocket error: {error}")

# WebSocket close handler
def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

# WebSocket connection handler
def on_open(ws):
    print("WebSocket connected")
    subscribe_message = {
      "op": "subscribe",
      "args": [
        {"channel": "tickers", "instId": BTC_SPOT_SYMBOL},
        {"channel": "tickers", "instId": BTC_SWAP_SYMBOL},
      ],
    }
    ws.send(json.dumps(subscribe_message))


# Function to start the WebSocket
def start_websocket():
    global ws
    ws = websocket.WebSocketApp(
        OKX_WS_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    redis_client.set("position_open", "false")
    websocket_thread = threading.Thread(target=start_websocket)
    websocket_thread.start()
    while True:
      time.sleep(600) # keep main thread alive
