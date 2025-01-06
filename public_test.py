import asyncio
import time
import json
from okx.websocket.WsPublicAsync import WsPublicAsync


def publicCallback(message):
    global spot_count
    global swap_count
    res = json.loads(message)
    res = dict(res)
    try:
        ts = res['data'][0]['ts']
        now = int(int(time.time()/10) * 1e4)
        print(now - int(ts))
    except Exception:
        print('failed')
#    if res['arg']['instId'] == 'BTC-USDT':
#        spot_count = spot_count + 1
#    elif res['arg']['instId'] == 'BTC-USDT-SWAP':
#        swap_count = swap_count + 1
#    else:
#        pass

spot_count = 0
swap_count = 0
async def main():
    url = "wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999"
    ws = WsPublicAsync(url=url)
    await ws.start()
    args = []
    arg1 = {"channel": "trades", "instId": "BTC-USDT-SWAP"}
#    arg1 = {"channel": "candle1s", "instId": "BTC-USDT-SWAP"}
    arg2 = {"channel": "tickers", "instId": "BTC-USDT-SWAP"}
    args.append(arg1)
    args.append(arg2)
    await ws.subscribe(args, publicCallback)
    await asyncio.sleep(60)
    print("-----------------------------------------unsubscribe all--------------------------------------------")
    await ws.unsubscribe(args, publicCallback)
    print(f"get {spot_count} spot messages")
    print(f"get {swap_count} swap messages")


if __name__ == '__main__':
    asyncio.run(main())
