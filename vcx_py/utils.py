#  Copyright (c) 2024 Aaron Janeiro Stone
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from hashlib import md5
from typing import Union

from vcx_py.constants import TYPICAL_KEY_TO_ENUM, ATYPICAL_KEY_TO_ENUM


class VirgoCXException(Exception):
    """
    Base exception for the VirgoCX API.
    """
    pass  # overrides allow for optional fine-grained control


class VirgoCXStatusException(VirgoCXException):
    """
    Non-200 status code returned from the VirgoCX API request.
    """
    pass


class VirgoCXAPIError(VirgoCXException):
    """
    Error code returned from the VirgoCX API request.
    """
    pass


def output_enumify(inp: Union[dict, list], typical: bool = True) -> Union[dict, list]:
    """
    Converts dictionary values to their respective enums.
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
        return [output_enumify(i, typical) for i in inp]
    return inp


def vcx_sign(dct: dict, api_secret: str = None) -> str:
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


def result_formatter(typical_map: bool = True) -> callable:
    """
    Handles the response from the VirgoCX API.
    """

    def outer(fn: callable) -> callable:
        def inner(*args, **kwargs) -> Union[dict, list]:
            res = fn(*args, **kwargs)
            if res.status_code != 200:
                raise VirgoCXStatusException(f"Request failed with status code {res.status_code}: {res.text}")
            res = res.json()
            if res["code"] != 0:
                raise VirgoCXAPIError(f"Request failed with error code {res['code']}: {res}")
            res = res["data"]
            return output_enumify(res, typical_map)

        return inner

    return outer


__all__ = ["VirgoCXException", "VirgoCXStatusException", "VirgoCXAPIError", "output_enumify", "vcx_sign",
           "result_formatter"]
