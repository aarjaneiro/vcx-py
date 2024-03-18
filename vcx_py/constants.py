#  Copyright (c) 2024 Aaron Janeiro Stone
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from enum import IntEnum

# Because CloudFlare is may block when accessed via the domain name, the IP address is used instead for now.
ROOT_ADDRESS = "https://3.98.238.66/api"
"""The root address of the VirgoCX API."""

# Once the CloudFlare issue is resolved, the domain name will be used instead of the IP and the following
# can be set to True.
VERIFICATION = False
"""Whether or not to verify the SSL certificate of the VirgoCX API."""


class KLineType(IntEnum):
    """
    Enum for the type of kline.
    """
    MINUTE = 1
    FIVE_MINUTE = 5
    TEN_MINUTE = 10
    THIRTY_MINUTE = 30
    HOUR = 60
    FOUR_HOUR = 240
    DAY = 1440
    FIVE_DAY = 7200
    WEEK = 10080
    MONTH = 43200


class OrderStatus(IntEnum):
    """
    Enum for the status of an order.
    """
    CANCELED = -1
    PLACED = 0
    OPEN = 1
    MATCHING = 2
    COMPLETED = 3


class OrderDirection(IntEnum):
    """
    Enum for the direction of an order.
    """
    BUY = 1
    SELL = 2

    @classmethod
    def from_str(cls, s: str):
        if s.lower() == "buy":
            return cls.BUY
        elif s.lower() == "sell":
            return cls.SELL
        raise ValueError(f"Invalid order direction: {s}")


class OrderType(IntEnum):
    """
    Enum for the type of an order.
    """
    LIMIT = 1
    MARKET = 2
    QUICK_TRADE = 3


TYPICAL_KEY_TO_ENUM = {
    "status": OrderStatus,
    "direction": OrderDirection,
    "type": OrderType
}
"""
Mapping of keys to enums in the typical case.
"""

ATYPICAL_KEY_TO_ENUM = {
    "status": OrderStatus,
    "category": OrderType,
    "type": OrderDirection.from_str
}
"""
Mapping of keys to enums in the atypical case.
"""


class Enums:
    """
    VirgoCX API enums.
    """
    KLineType = KLineType
    OrderStatus = OrderStatus
    OrderDirection = OrderDirection
    OrderType = OrderType
