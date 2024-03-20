#  Copyright (c) 2024 Aaron Janeiro Stone
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from typing import Optional

import requests as rq

from .constants import ROOT_ADDRESS, VERIFICATION, KLineType, OrderStatus, \
    OrderType, OrderDirection
from .utils import vcx_sign, result_formatter


class VirgoCXClient:
    def __init__(self, api_key: str = None, api_secret: str = None):
        # Prevents the api key and secret from being visible as class attributes
        def _api_key():
            return api_key

        def signer(dct: dict):
            return vcx_sign(dct, api_secret)

        self.signer = signer
        self._api_key = _api_key

    @result_formatter()
    def kline(self, symbol: str, period: KLineType):
        """
        Returns the kline data for a given symbol and period.

        :param symbol: The symbol to query.
        :param period: How the kline data should be aggregated.
        """
        if isinstance(period, KLineType):
            period = period.value
        return rq.get(f"{ROOT_ADDRESS}/market/history/kline", params={"symbol": symbol, "period": period},
                      verify=VERIFICATION)

    @result_formatter()
    def ticker(self, symbol: str):
        """
        Returns the ticker data for a given symbol.

        :param symbol: The symbol to query.
        """
        return rq.get(f"{ROOT_ADDRESS}/market/detail/merged", params={"symbol": symbol}, verify=VERIFICATION)

    @result_formatter()
    def tickers(self):
        """
        Returns the ticker data for all symbols.
        """
        return rq.get(f"{ROOT_ADDRESS}/market/tickers", verify=VERIFICATION)

    @result_formatter()
    def account_info(self):
        """
        Returns the account information.
        """
        payload = {"apiKey": self._api_key()}
        payload["sign"] = self.signer(payload)
        return rq.get(f"{ROOT_ADDRESS}/member/accounts", params=payload, verify=VERIFICATION)

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
        return rq.get(f"{ROOT_ADDRESS}/member/queryOrder", params=payload, verify=VERIFICATION)

    @result_formatter(False)
    def query_trades(self, symbol: str):
        """
        Returns (completed) user trades for a given symbol.

        :param symbol: The symbol to query.
        """
        payload = {"apiKey": self._api_key(), "symbol": symbol}
        payload["sign"] = self.signer(payload)
        return rq.get(f"{ROOT_ADDRESS}/member/queryTrade", params=payload, verify=VERIFICATION)

    @result_formatter()
    def place_order(self, symbol: str, category: OrderType, direction: OrderDirection,
                    price: Optional[float] = None, qty: Optional[float] = None,
                    total: Optional[float] = None):
        """
        Places an order.

        :param symbol: The symbol to place the order for.
        :param category: The type of order to place.
        :param direction: The direction of the order.
        :param price: The price of the order (optional).
        :param qty: The quantity of the order in terms of the cryptocurrency (optional).
        :param total: The total value of the order in terms of the fiat currency (optional).

        Note that `price` is required for limit orders and `total` is required for non-limit buy orders
        (otherwise `qty` is required).
        """
        if isinstance(category, OrderType):
            category = category.value
        if isinstance(direction, OrderDirection):
            direction = direction.value

        if category == OrderType.LIMIT:
            if price is None:
                raise ValueError("Price is required for limit orders")
            if qty is None:
                raise ValueError("Quantity is required for limit orders")
        else:
            if total is None and direction == OrderDirection.BUY:
                raise ValueError("Total is required for non-limit buy orders")

        payload = {"apiKey": self._api_key(), "symbol": symbol, "category": category, "type": direction,
                   "country": 1}
        if price is not None:
            payload["price"] = price
        if qty is not None:
            payload["qty"] = qty
        if total is not None:
            payload["total"] = total
        payload["sign"] = self.signer(payload)
        return rq.post(f"{ROOT_ADDRESS}/member/addOrder", data=payload, verify=VERIFICATION)

    @result_formatter()
    def cancel_order(self, order_id: str):
        """
        Cancels an order.

        :param order_id: The ID of the order to cancel.
        """
        payload = {"apiKey": self._api_key(), "id": order_id}
        payload["sign"] = self.signer(payload)
        return rq.post(f"{ROOT_ADDRESS}/member/cancelOrder", data=payload, verify=VERIFICATION)

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
        return rq.get(f"{ROOT_ADDRESS}/member/discountPrice", params=payload, verify=VERIFICATION)
