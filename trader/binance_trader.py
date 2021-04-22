import math
import os

from binance.client import Client

from dotenv import load_dotenv
from trader_logger import logger

load_dotenv('config_paramter.env')

print(os.environ['API_KEY'])
print(os.environ['API_SECRET'])

class BinanceTrader:
    """
    Manager for buy and sell market order from binance
    """

    def __init__(self):
        if not os.environ['API_KEY'] or not os.environ['API_SECRET']:
            raise ValueError('The API key and API Secret is required')
        self._client = Client(api_key=os.environ['API_KEY'], api_secret=os.environ['API_SECRET'], tld='com')
        # self._client.API_URL = 'https://testnet.binance.vision/api'

    def sell_order(self, asset):
        """
        Market sell order for specific asset.
        :param asset: string asset symbol for example "BTC"
        :type asset:str
        """
        asset_symbol = f"{asset}USDT"
        balance = self._get_account_balance(asset)

        try:

            if balance > 0:
                info = self._client.get_symbol_info(asset_symbol)
                step_size = 0.0
                for f in info['filters']:
                    if f['filterType'] == 'LOT_SIZE':
                        step_size = float(f['stepSize'])
                precision = int(round(-math.log(step_size, 10), 0))
                quantity = float(round(balance, precision))
                quantity = quantity*0.95 # Binance commision



                logger.rootLogger.info("About to sell %s out of %s", str(quantity), str(balance))
                response = self._client.order_market_sell(
                    symbol=asset_symbol,
                    quantity=quantity,
                    recvWindow=50000
                )
                status = str(response['status'])
                if status and status.lower() == 'FILLED'.lower():
                    order_id = response['orderId']
                    orig_qty = response['origQty']
                    executed_qty = response['executedQty']
                    logger.rootLogger.info(
                        "sell order for %s filled with the order id %s qty %s exec_qty %s",
                        asset, str(order_id), str(orig_qty), str(executed_qty),
                        exc_info=1)
                else:
                    logger.rootLogger.critical('sell order fail for %s with the amount %s',
                                               asset, balance, exc_info=1)

        except:
            pass


        else:
            raise ValueError(f'No sufficient balance for {asset}')

    def buy_order(self, asset):
        """
        Market sell order for specific asset.
        :param asset: string asset symbol for example "BTC"
        :type asset:str
        :return:
        """

        try:

            balance = self._get_account_balance('USDT')
            if balance == 0.0:
                raise ValueError(f'No sufficient balance for {asset}')

            amount = (20 / 100) * balance

            if amount == 0:
                raise ValueError(f'When I take 20% of your account assets USDT I can\'t Buy {asset}')

            if amount < 10:
                amount = 10

            symbol = f'{asset}USDT'
            info = self._client.get_symbol_info(symbol)
            precision = info["quotePrecision"]
            if precision is None or precision == 0:
                precision = 6
            response = self._client.order_market_buy(
                symbol=symbol,
                quoteOrderQty=float(round(amount, precision)),
                recvWindow=50000
            )
            status = str(response['status'])
            if status and status.lower() == 'FILLED'.lower():
                order_id = response['orderId']
                orig_qty = response['origQty']
                executed_qty = response['executedQty']
                logger.rootLogger.info(
                    "buy order for %s filled with the order id %s qty %s exec_qty %s",
                    asset, str(order_id), str(orig_qty), str(executed_qty),
                    exc_info=1)
            else:
                logger.rootLogger.critical('buy order fail for %s with the amount %s',
                                           asset, balance, exc_info=1)

        except:
            pass

    def _get_account_balance(self, asset):
        """
        Get the current account balance
        :param asset: string asset symbol for example "BTC"
        :type asset:str
        :return: 0 if no asset found or asset value float.
        """
        balance = self._client.get_asset_balance(asset=f"{asset}")
        logger.rootLogger.info("Account Balance ---> {}".format(balance))
        if balance is not None:
            return float(balance['free'])
        else:
            return 0
