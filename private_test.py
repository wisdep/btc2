import asyncio

from okx.websocket.WsPrivateAsync import WsPrivateAsync
from keys import *

def privateCallback(message):
    print("privateCallback", message)


async def main():
    #url = "wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999"
    url = "wss://wsaws.okx.com:8443/ws/v5/private"
    ws = WsPrivateAsync(
        apiKey= API_KEY,
        passphrase=PASS_PHRASE,
        secretKey=SECRET,
        url=url,
        useServerTime=False
    )
    await ws.start()
    args = []
    arg1 = {"channel": "account", "ccy": "USDT"}
#    arg2 = {"channel": "orders", "instType": "ANY"}
#    arg1 = {"channel": "balance_and_position"}
    args.append(arg1)
#    args.append(arg2)
#    args.append(arg3)
    await ws.subscribe(args, callback=privateCallback)
    await asyncio.sleep(5)
    print("-----------------------------------------unsubscribe all--------------------------------------------")
#    args3 = [arg1, arg3]
    await ws.unsubscribe(args, callback=privateCallback)


if __name__ == '__main__':
    asyncio.run(main())
