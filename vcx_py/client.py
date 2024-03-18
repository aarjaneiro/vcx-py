#  Copyright (c) 2024 Aaron Janeiro Stone
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from hashlib import md5
from typing import Union, Optional

import requests as rq

from .constants import TYPICAL_KEY_TO_ENUM, ATYPICAL_KEY_TO_ENUM, ROOT_ADDRESS, VERIFICATION, KLineType, OrderStatus, \
    OrderType, OrderDirection


def _output_enumify(inp: Union[dict, list], typical: bool = True) -> Union[dict, list]:
    """
    Converts the keys in a dictionary to their respective enums.
    """
    mapping = TYPICAL_KEY_TO_ENUM if typical else ATYPICAL_KEY_TO_ENUM
    if isinstance(inp, dict):
        out = {}
        for k, v in inp.items():
            if k in mapping:
                out[k] = mapping[k](v)
            else:
                out[k] = v
        return out
    elif isinstance(inp, list):
        return [_output_enumify(i, typical) for i in inp]
    return inp


def vcx_sig(dct: dict, api_secret: str = None) -> str:
    """
    Returns the signature required for an authenticated VirgoCX API request.
    """
    _dct = dct.copy()
    if "apiSecret" not in _dct:
        if api_secret is None:
            raise ValueError("API secret is required")
        _dct["apiSecret"] = api_secret
    val_str = ""
    for k in sorted(_dct.keys()):
        val_str += str(_dct[k])
    return md5(val_str.encode()).hexdigest()


def _res_handler(typical_map: bool = True):
    """
    Handles the response from the VirgoCX API.
    """

    def outer(fn: callable):
        def inner(*args, **kwargs):
            res = fn(*args, **kwargs)
            if res.status_code != 200:
                raise ValueError(f"Request failed with status code {res.status_code}: {res.text}")
            res = res.json()
            if res["code"] != 0:
                raise ValueError(f"Request failed with error code {res['code']}: {res['msg']}")
            res = res["data"]
            return _output_enumify(res, typical_map)

        return inner

    return outer


class VirgoCXClient:
    def __init__(self, api_key: str = None, api_secret: str = None):
        # Prevents the api key and secret from being visible as class attributes
        def _api_key():
            return api_key

        def signer(dct: dict):
            return vcx_sig(dct, api_secret)

        self.signer = signer
        self._api_key = _api_key

    @_res_handler()
    def kline(self, symbol: str, period: KLineType) -> rq.Response:
        """
        Returns the kline data for a given symbol and period.

        :param symbol: The symbol to query.
        :param period: How the kline data should be aggregated.
        """
        if isinstance(period, KLineType):
            period = period.value
        return rq.get(f"{ROOT_ADDRESS}/market/history/kline", params={"symbol": symbol, "period": period},
                      verify=VERIFICATION)

    @_res_handler()
    def ticker(self, symbol: str) -> rq.Response:
        """
        Returns the ticker data for a given symbol.

        :param symbol: The symbol to query.
        """
        return rq.get(f"{ROOT_ADDRESS}/market/detail/merged", params={"symbol": symbol}, verify=VERIFICATION)

    @_res_handler()
    def tickers(self) -> rq.Response:
        """
        Returns the ticker data for all symbols.
        """
        return rq.get(f"{ROOT_ADDRESS}/market/tickers", verify=VERIFICATION)

    @_res_handler()
    def account_info(self) -> rq.Response:
        """
        Returns the account information.
        """
        payload = {"apiKey": self._api_key()}
        payload["sign"] = self.signer(payload)
        return rq.get(f"{ROOT_ADDRESS}/member/accounts", params=payload, verify=VERIFICATION)

    @_res_handler()
    def query_orders(self, symbol: str, status: Optional[OrderStatus] = None) -> rq.Response:
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

    @_res_handler(False)
    def query_trades(self, symbol: str) -> rq.Response:
        """
        Returns (completed) user trades for a given symbol.

        :param symbol: The symbol to query.
        """
        payload = {"apiKey": self._api_key(), "symbol": symbol}
        payload["sign"] = self.signer(payload)
        return rq.get(f"{ROOT_ADDRESS}/member/queryTrade", params=payload, verify=VERIFICATION)

    @_res_handler()
    def place_order(self, symbol: str, category: OrderType, direction: OrderDirection,
                    price: Optional[float] = None, qty: Optional[float] = None,
                    total: Optional[float] = None) -> rq.Response:
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
        elif total is None and direction == OrderDirection.BUY:
            raise ValueError("Total is required for non-limit buy orders")
        elif qty is None:
            raise ValueError("Quantity is required for all but non-limit buy orders")

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

    @_res_handler()
    def cancel_order(self, order_id: str) -> rq.Response:
        """
        Cancels an order.

        :param order_id: The ID of the order to cancel.
        """
        payload = {"apiKey": self._api_key(), "id": order_id}
        payload["sign"] = self.signer(payload)
        return rq.post(f"{ROOT_ADDRESS}/member/cancelOrder", data=payload, verify=VERIFICATION)

    @_res_handler()
    def get_discount(self, symbol: Optional[str] = None) -> rq.Response:
        """
        Returns the discount for a given symbol (or all symbols if one is not provided).

        :param symbol: The symbol to query (optional).
        """
        payload = {"apiKey": self._api_key()}
        if symbol is not None:
            payload["symbol"] = symbol
        payload["sign"] = self.signer(payload)
        return rq.get(f"{ROOT_ADDRESS}/member/discountPrice", params=payload, verify=VERIFICATION)
