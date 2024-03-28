#  Copyright (c) 2024 Aaron Janeiro Stone
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from typing import Optional
from threading import Lock
from warnings import warn

import requests as rq

from .constants import ROOT_ADDRESS, VERIFICATION, KLineType, OrderStatus, \
    OrderType, OrderDirection
from .utils import VirgoCXWarning, VirgoCXException, vcx_sign, result_formatter


class VirgoCXClient:
    """
    A simple python client for the VirgoCX API.
    """
    FMT_DATA = None  # created by first instance
    STATIC_LOCK = Lock()  # in case of multithreading, locks the formatting cache
    ENDPOINT = ROOT_ADDRESS  # can be changed for testing

    def __init__(self, api_key: str = None, api_secret: str = None):
        # Prevents the api key and secret from being visible as class attributes
        def _api_key():
            return api_key

        def signer(dct: dict):
            return vcx_sign(dct, api_secret)

        self.signer = signer
        self._api_key = _api_key

        with VirgoCXClient.STATIC_LOCK:
            if VirgoCXClient.FMT_DATA is None:
                VirgoCXClient.FMT_DATA = {v["symbol"]: {"price_decimals": v["priceDecimals"],
                                                        "qty_decimals": v["qtyDecimals"],
                                                        "min_total": v["minTotal"]} for v in
                                          self.tickers()}

    @result_formatter()
    def kline(self, symbol: str, period: KLineType):
        """
        Returns the kline data for a given symbol and period.

        :param symbol: The symbol to query.
        :param period: How the kline data should be aggregated.
        """
        if isinstance(period, KLineType):
            period = period.value
        return rq.get(f"{self.ENDPOINT}/market/history/kline", params={"symbol": symbol, "period": period},
                      verify=VERIFICATION)

    @result_formatter()
    def ticker(self, symbol: str):
        """
        Returns the ticker data for a given symbol.

        :param symbol: The symbol to query.
        """
        return rq.get(f"{self.ENDPOINT}/market/detail/merged", params={"symbol": symbol}, verify=VERIFICATION)

    @result_formatter()
    def tickers(self):
        """
        Returns the ticker data for all symbols.
        """
        return rq.get(f"{self.ENDPOINT}/market/tickers", verify=VERIFICATION)

    @result_formatter()
    def account_info(self):
        """
        Returns the account information.
        """
        payload = {"apiKey": self._api_key()}
        payload["sign"] = self.signer(payload)
        return rq.get(f"{self.ENDPOINT}/member/accounts", params=payload, verify=VERIFICATION)

    @result_formatter()
    def query_orders(self, symbol: str, status: Optional[OrderStatus] = None):
        """
        Returns user orders for a given symbol and status.

        :param symbol: The symbol to query.
        :param status: Restrict the query to this specific status (optional).
        """
        payload = {"apiKey": self._api_key(), "symbol": symbol}
        if status is not None:
            if isinstance(status, OrderStatus):
                status = status.value
            payload["status"] = status
        payload["sign"] = self.signer(payload)
        return rq.get(f"{self.ENDPOINT}/member/queryOrder", params=payload, verify=VERIFICATION)

    @result_formatter(False)
    def query_trades(self, symbol: str):
        """
        Returns (completed) user trades for a given symbol.

        :param symbol: The symbol to query.
        """
        payload = {"apiKey": self._api_key(), "symbol": symbol}
        payload["sign"] = self.signer(payload)
        return rq.get(f"{self.ENDPOINT}/member/queryTrade", params=payload, verify=VERIFICATION)

    @result_formatter()
    def place_order(self, symbol: str, category: OrderType, direction: OrderDirection,
                    price: Optional[float] = None, qty: Optional[float] = None,
                    total: Optional[float] = None, handle_conversions: bool = True,
                    **kwargs):
        """
        Places an order.

        :param symbol: The symbol to place the order for.
        :param category: The type of order to place.
        :param direction: The direction of the order.
        :param price: The price of the order (optional).
        :param qty: The quantity of the order in terms of the cryptocurrency (optional).
        :param total: The total value of the order in terms of the fiat currency (optional).
        :param handle_conversions: Whether to handle conversions between `qty`, and `total` (optional, default True).
                                   Might require additional API calls in order to determine the market price.

        Note that without `handle_conversions`, `price` is required for limit orders and `total` is required for
        non-limit buy orders (otherwise `qty` is required).
        """
        if isinstance(category, OrderType):
            category = category.value
        if isinstance(direction, OrderDirection):
            direction = direction.value

        # Handle conversions
        if category == OrderType.LIMIT:
            if price is None:
                raise ValueError("Price is required for limit orders")
            if qty is None:
                if not handle_conversions:
                    raise ValueError("Quantity is required for limit orders")
                else:
                    qty = total / price
                    total = None
        else:  # i.e., quick trade or market order
            if total is None and direction == OrderDirection.BUY:
                if not handle_conversions:
                    raise ValueError("Total is required for non-limit buy orders")
                else:
                    market_price = kwargs.get("market_price", None)
                    if market_price is None:
                        market_price = self.__extract_market_price__(direction, symbol)
                    total = qty * market_price
                    qty = None

        payload = {"apiKey": self._api_key(), "symbol": symbol, "category": category, "type": direction,
                   "country": 1}

        with VirgoCXClient.STATIC_LOCK:
            if symbol in VirgoCXClient.FMT_DATA:
                fmt_data = VirgoCXClient.FMT_DATA[symbol]
            else:
                raise VirgoCXException(f"Symbol {symbol} not found in formatting cache")

        # Format and check values
        if price is not None:
            price = float(price)  # can be int which breaks decimal places check
            if len(str(price).split(".")[1]) > fmt_data["price_decimals"]:
                warn(f"Price {price} has more than {fmt_data['price_decimals']} decimal places. Correcting...",
                     VirgoCXWarning)
                price = round(price, fmt_data["price_decimals"])
            payload["price"] = price

        if qty is not None:
            qty = float(qty)
            if len(str(qty).split(".")[1]) > fmt_data["qty_decimals"]:
                warn(f"Quantity {qty} has more than {fmt_data['qty_decimals']} decimal places. Correcting...",
                     VirgoCXWarning)
                qty = round(qty, fmt_data["qty_decimals"])
            payload["qty"] = qty

        if total is not None:
            total = float(total)
            if total < fmt_data["min_total"]:
                raise ValueError(f"Total {total} is below the minimum allowed {fmt_data['min_total']}")
            if len(str(total).split(".")[1]) > fmt_data["price_decimals"]:
                warn(f"Total {total} has more than {fmt_data['price_decimals']} decimal places. Correcting...",
                     VirgoCXWarning)
                total = round(total, fmt_data["price_decimals"])
            payload["total"] = total

        # Sign and send request
        payload["sign"] = self.signer(payload)
        return rq.post(f"{self.ENDPOINT}/member/addOrder", data=payload, verify=VERIFICATION)

    def __extract_market_price__(self, direction, symbol):
        market_price = self.get_discount(symbol=symbol)[0]
        if direction == OrderDirection.BUY:
            market_price = float(market_price["Ask"])
        else:
            market_price = float(market_price["Bid"])
        return market_price

    @result_formatter()
    def cancel_order(self, order_id: str):
        """
        Cancels an order.

        :param order_id: The ID of the order to cancel.
        """
        payload = {"apiKey": self._api_key(), "id": order_id}
        payload["sign"] = self.signer(payload)
        return rq.post(f"{self.ENDPOINT}/member/cancelOrder", data=payload, verify=VERIFICATION)

    @result_formatter()
    def get_discount(self, symbol: Optional[str] = None):
        """
        Returns similar output as `ticker` for a given symbol (or all symbols if one is not provided) with
        your account discount applied to prices.

        Note that this method always returns a list of dictionaries, even if only one symbol is queried.

        :param symbol: The symbol to query (optional).
        """
        payload = {"apiKey": self._api_key()}
        if symbol is not None:
            payload["symbol"] = symbol
        payload["sign"] = self.signer(payload)
        return rq.get(f"{self.ENDPOINT}/member/discountPrice", params=payload, verify=VERIFICATION)
