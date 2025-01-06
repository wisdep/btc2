import okx.MarketData as MarketData
import pandas as pd
from datetime import datetime as dt
import time

flag = "0"  # 实盘:0 , 模拟盘：1
b_time = 1704067200000
symbols = [
           # 'BTC-USDT-SWAP',
           # 'BTC-USDT',
           # 'ETH-USDT-SWAP',
           # 'ETH-USDT',
           #'DOGE-USDT-SWAP',
#           'DOGE-USDT',
#           'SOL-USDT-SWAP',
#           'SOL-USDT',
#           'XRP-USDT-SWAP',
           'XRP-USDT']

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# 获取标记价格K线数据
def get_candle(timestamp):
    result = marketDataAPI.get_history_candlesticks(
        instId=symbol,
        bar='1m',
        after=timestamp
    )
    df = pd.DataFrame(result['data']
                      , columns = ['time', 'open', 'high', 'low', 'close', 'vol','volCcy','volCcyQuote','confirm']
                     )
    df['timestamp'] = df['time']
    df['time'] = pd.to_datetime(df['time'].astype(float),unit = 'ms')
    return df

for symbol in symbols:
    now = int(int(time.time()/10) * 1e4)
    df = pd.DataFrame()
    while now >= b_time:
        temp = get_candle(now)
        length = temp.shape[0]
        now = int(now - 6 * 1e4 * 100)
        df = pd.concat([df,temp])
        time.sleep(0.1)
    df.to_csv(f'data/{symbol}.csv', index=None)
