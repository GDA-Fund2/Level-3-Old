import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json
from pricebybit import PriceBybit, TOPIC_BYBIT_INSURANCE, TOPIC_BYBIT_KLINE, TOPIC_BYBIT_OB200, TOPIC_BYBIT_TRADE
from pricebybitusdt import PriceBybitUSDT, TOPIC_BYBIT_USDT_CANDLE, TOPIC_BYBIT_USDT_OB200, TOPIC_BYBIT_USDT_TRADE
from pricebinance import PriceBinance, TOPIC_BINANCE_BINANCE

EX_BYBIT        = "ByBit"
EX_BYBIT_USDT   = "ByBit-USDT"
EX_BINANCE      = "Binanace"
EX_COINBASE     = "Coinbase"

TOPIC_COINBASE_BTCUSD   = "BTC-USD"
TOPIC_COINBASE_ETHUSD   = "ETH-USD"

class PriceInfo(object):
    def __init__(self):
        self.log = log_json()

    def getJson(self, symbol:str, price:float, timestamp:int):
        date = datetime.datetime.fromtimestamp(timestamp / 1e3).isoformat()
        return {
            "symbol"    : symbol,
            "price"     : price,
            "timestamp" : timestamp       
        }

    def process_raw_data(self, exchange:str, topic:str, data):
        json_data = {}
        try:
            json_data = str_to_json(data)
        except Exception as ex:
            self.log.create("ERROR", str(ex))
            return(None)

        if EX_BYBIT         == exchange:        return PriceBybit().process_json_data(topic=topic, json_data=json_data)
        if EX_BYBIT_USDT    == exchange:        return PriceBybitUSDT().process_json_data(topic=topic, json_data=json_data)
        # if EX_COINBASE      == exchange:        return PriceCoinBase().process_json_data(topic=topic, json_data=json_data)
        if EX_BINANCE       == exchange:        return PriceBinance().process_json_data(topic=topic, json_data=json_data)

        self.log.create("ERROR", f'{exchange} EXCHANGE NOT SUPPOTED')
        return None
    
    def test_it():
        pass

if __name__ == '__main__':
    info = PriceInfo()

    raw_data = "{\"topic\":\"insurance.ETH\",\"data\":[{\"currency\":\"ETH\",\"timestamp\":\"2021-10-15T20:00:00Z\",\"wallet_balance\":4832029953542}]}"
    print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_INSURANCE,raw_data))
    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_KLINE,raw_data))
    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_OB200,raw_data))
    raw_data = "{\"topic\":\"trade.XRPUSD\",\"data\":[{\"trade_time_ms\":1634342763132,\"timestamp\":\"2021-10-16T00:06:03.000Z\",\"symbol\":\"XRPUSD\",\"side\":\"Sell\",\"size\":1094,\"price\":1.1441,\"tick_direction\":\"MinusTick\",\"trade_id\":\"a6aa635a-89f7-5fd5-a29d-df9f0b13d937\",\"cross_seq\":3780829306},{\"trade_time_ms\":1634342763132,\"timestamp\":\"2021-10-16T00:06:03.000Z\",\"symbol\":\"XRPUSD\",\"side\":\"Sell\",\"size\":200,\"price\":1.1441,\"tick_direction\":\"ZeroMinusTick\",\"trade_id\":\"ea2dcc4c-26f4-5a19-ba7b-2fc187b9b37b\",\"cross_seq\":3780829306},{\"trade_time_ms\":1634342763132,\"timestamp\":\"2021-10-16T00:06:03.000Z\",\"symbol\":\"XRPUSD\",\"side\":\"Sell\",\"size\":4,\"price\":1.1441,\"tick_direction\":\"ZeroMinusTick\",\"trade_id\":\"aeaeaa83-79cb-5f80-887f-9e527153b6fb\",\"cross_seq\":3780829306},{\"trade_time_ms\":1634342763132,\"timestamp\":\"2021-10-16T00:06:03.000Z\",\"symbol\":\"XRPUSD\",\"side\":\"Sell\",\"size\":9735,\"price\":1.1439,\"tick_direction\":\"MinusTick\",\"trade_id\":\"b3942a44-639c-5365-a82b-7ac67dd097e4\",\"cross_seq\":3780829306}]}"
    print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_TRADE,raw_data))

    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_BYBIT_USDT,TOPIC_BYBIT_USDT_CANDLE,raw_data))
    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_BYBIT_USDT,TOPIC_BYBIT_USDT_OB200,raw_data))
    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_BYBIT_USDT,TOPIC_BYBIT_USDT_TRADE,raw_data))

    # print(info.process_raw_data(EX_COINBASE,TOPIC_COINBASE_BTCUSD,raw_data))
    # print(info.process_raw_data(EX_COINBASE,TOPIC_COINBASE_ETHUSD,raw_data))

    raw_data = "{\"stream\":\"btcusdt@aggTrade\",\"data\":{\"e\":\"aggTrade\",\"E\":1634390640539,\"a\":874355956,\"s\":\"BTCUSDT\",\"p\":\"60602.22\",\"q\":\"0.002\",\"f\":1546375311,\"l\":1546375311,\"T\":1634390640533,\"m\":false}}"
    print(info.process_raw_data(EX_BINANCE,TOPIC_BINANCE_BINANCE,raw_data))
