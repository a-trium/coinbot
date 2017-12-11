#!/usr/bin/python
# -*- coding: 949 -*-
import requests
import logging
import time
from decimal import *
from datetime import datetime, timezone
from dateutil import tz

def get_datetime_kst_now():
  return datetime.now(timezone.utc).astimezone(tz.gettz("Asia/Seoul"))


## setting logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler()) # is Test


## time
dt_kst_now = get_datetime_kst_now().replace(second=0, microsecond=0)
dt_str_kst = dt_kst_now.strftime("%Y-%m-%d %H:%M:%S")
timestamp = Decimal(int(dt_kst_now.timestamp()))
logger.info("datetime_kst:{} timestamp:{}".format(dt_kst_now, timestamp))


## getting
API_TICKER_POLONIEX = "https://poloniex.com/public?command=returnTicker"
available_currency = {
  "BTC": "USDT_BTC",
  "ETH": "USDT_ETH",
  # "ETC": "USDT_ETC",
  # "XRP": "USDT_XRP",
  # "LTC": "USDT_LTC",
  # "DASH": "USDT_DASH",
  # "NXT": "USDT_NXT",
  # "STR": "USDT_STR",
  # "XMR": "USDT_XMR",
  # "REP": "USDT_REP",
  # "ZEC": "USDT_ZEC",
}
COINS_POLONIEX = list(available_currency.keys())

response = requests.get(API_TICKER_POLONIEX)
tickers = response.json()

for coin_meta in COINS_POLONIEX:
  currency = available_currency[coin_meta]
  price_usd = tickers[currency]["lowestAsk"] # use lowestAsk as price
  volume = tickers[currency]["quoteVolume"]
  bid = tickers[currency]["highestBid"]
  ask = tickers[currency]["lowestAsk"]
  percent_change_price_usd = tickers[currency]["percentChange"]

  # log
  logger.info(" - {}, {} $".format(coin_meta, price_usd))
  # logger.info(" - {} currency:{} price_usd:{} volume:{} ask:{} bid:{} percent_change_price_usd:{}".format(
  #   coin_meta, currency, price_usd, volume, ask, bid, percent_change_price_usd
  # ))



## getting coinone API
# - http://doc.coinone.co.kr/#api-Public-Ticker
API_TICKER_COINONE = "https://api.coinone.co.kr/ticker?currency=all"
COINS_COINONE = ["btc", "eth"]

response = requests.get(API_TICKER_COINONE)
tickers = response.json()
timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Decimal(tickers["timestamp"])))

logger.info("time : {}".format(timestamp))

## formatting each coin data
for coin_meta in COINS_COINONE:

  coin = tickers[coin_meta]
  coin_name = coin["currency"].upper()
  coin_krw = coin["last"]

  # logger.info(" - coin: {}".format(coin))
  logger.info(" - {}, {} KRW".format(coin_name, coin_krw))
  # btc = ticker["btc"]
  # logger.info("coin:{}, timestamp: {}, price_krw:{}".format(
  #     btc["currency"].upper(), Decimal(ticker["timestamp"]), btc["last"]
  # ))



yahoo_usd_to_krw_url = 'http://query.yahooapis.com/v1/public/yql?q=select%20%2a%20from%20yahoo.finance.xchange%20where%20pair%20in%20%28%22USDKRW%22%29&format=json&env=store://datatables.org/alltableswithkeys'
response = requests.get(yahoo_usd_to_krw_url).json()
logger.info("response: {}".format(response))
