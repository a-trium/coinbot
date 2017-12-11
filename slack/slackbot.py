import os
import time
from slackclient import SlackClient
import requests
import logging
import time
from decimal import *
from datetime import datetime, timezone
# from dateutil import tz

BOT_ID = os.environ.get("BOT_ID")
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "김치"

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

COINS = [
  "BTC",
  "ETH",
  "ETC",
  "XRP",
  "LTC",
  "BCH"
]

## setting logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler()) # is Test

# def get_datetime_kst_now():
#   return datetime.now(timezone.utc).astimezone(tz.gettz("Asia/Seoul"))


## getting poloniex API
# USD info
def get_coin_meta_form_poloniex():
  API_TICKER_POLONIEX = "https://poloniex.com/public?command=returnTicker"
  available_currency = {
    "BTC": "USDT_BTC",
    "ETH": "USDT_ETH",
    "ETC": "USDT_ETC",
    "XRP": "USDT_XRP",
    "LTC": "USDT_LTC",
    "BCH": "USDT_BCH",
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
  result = {}

  for coin_meta in COINS_POLONIEX:
    currency = available_currency[coin_meta]
    price_usd = tickers[currency]["lowestAsk"] # use lowestAsk as price
    volume = tickers[currency]["quoteVolume"]
    bid = tickers[currency]["highestBid"]
    ask = tickers[currency]["lowestAsk"]
    percent_change_price_usd = tickers[currency]["percentChange"]

    # log
    # logger.info(" - {}, {} $".format(coin_meta, price_usd))
    # logger.info(" - {} currency:{} price_usd:{} volume:{} ask:{} bid:{} percent_change_price_usd:{}".format(
    #   coin_meta, currency, price_usd, volume, ask, bid, percent_change_price_usd
    # ))
    # result[coin_meta] = int(float(price_usd))
    result[coin_meta] = (float(price_usd))

  return result

## getting coinone API
# - http://doc.coinone.co.kr/#api-Public-Ticker
def get_coin_meta_form_coinone():
  API_TICKER_COINONE = "https://api.coinone.co.kr/ticker?currency=all"
  COINS_COINONE = [
    "btc",
    "eth",
    "etc",
    "xrp",
    "ltc",
    "bch"
  ]

  response = requests.get(API_TICKER_COINONE)
  tickers = response.json()
  timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Decimal(tickers["timestamp"])))

  logger.info("time : {}".format(timestamp))
  result = {}

  ## formatting each coin data
  for coin_meta in COINS_COINONE:

    coin = tickers[coin_meta]
    coin_name = coin["currency"].upper()
    coin_krw = coin["last"]

    # logger.info(" - coin: {}".format(coin))
    # logger.info(" - {}, {} KRW".format(coin_name, coin_krw))
    # btc = ticker["btc"]
    # logger.info("coin:{}, timestamp: {}, price_krw:{}".format(
    #     btc["currency"].upper(), Decimal(ticker["timestamp"]), btc["last"]
    # ))
    result[coin_name] = coin_krw

  return result


## Exchange rate
def USD_TO_KRW_exchange_rate():
  usd_to_krw_url = 'https://api.manana.kr/exchange/rate.json'
  response = requests.get(usd_to_krw_url).json()
  return response[1]['rate']


def handle_command(command, channel):
  """
      Receives commands directed at the bot and determines if they
      are valid commands. If so, then acts on the commands. If not,
      returns back what it needs for clarification.
  """
  response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
             "* command with numbers, delimited by spaces."
  if command.startswith(EXAMPLE_COMMAND):

    ## time
    # dt_kst_now = get_datetime_kst_now().replace(microsecond=0)
    # dt_str_kst = dt_kst_now.strftime("%Y-%m-%d %H:%M:%S")
    # timestamp = Decimal(int(dt_kst_now.timestamp()))
    # logger.info("datetime_kst:{} timestamp:{}".format(dt_kst_now, timestamp))


    ## price info - USD, KRW
    price_usd = get_coin_meta_form_poloniex()
    price_krw = get_coin_meta_form_coinone()
    usd_to_krw = USD_TO_KRW_exchange_rate()

    #
    response = ""
    logger.info('----result----')
    for coin in COINS:
      krw = int(price_krw[coin])
      usd = int(price_usd[coin] * usd_to_krw)
      # print (coin, "{0:.3f}%".format((krw - usd)/usd * 100), krw, usd)

      logger.info(" - {} \t{}\t COINONE: {}\t, POLONIEX: {}".format(coin, "{0:.3f}%".format((krw - usd)/usd * 100), "{:,}".format(krw), "{:,}".format(usd)))
      response+=" - {} \t{}\t COINONE: {}\t, POLONIEX: {}\n".format(coin, "{0:.3f}%".format((krw - usd)/usd * 100), "{:,}".format(krw), "{:,}".format(usd))


  slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
  """
      The Slack Real Time Messaging API is an events firehose.
      this parsing function returns None unless a message is
      directed at the Bot, based on its ID.
  """
  output_list = slack_rtm_output
  if output_list and len(output_list) > 0:
    for output in output_list:
      if output and 'text' in output and AT_BOT in output['text']:
        # return text after the @ mention, whitespace removed
        return output['text'].split(AT_BOT)[1].strip().lower(), \
               output['channel']
  return None, None


if __name__ == "__main__":
  READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
  if slack_client.rtm_connect():
    print("StarterBot connected and running!")
    while True:
      command, channel = parse_slack_output(slack_client.rtm_read())
      if command and channel:
        handle_command(command, channel)
      time.sleep(READ_WEBSOCKET_DELAY)
  else:
    print("Connection failed. Invalid Slack token or bot ID?")