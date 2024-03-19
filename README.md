# VirgoCX Python Client

A simple Python client for the VirgoCX API.

For more information on the REST api on which this was built, please refer to the
[VirgoCX API Documentation](https://github.com/VirgocxDev/VirgocxApiDoc).

## Table of Contents

- [Setup](#setup)
    - [API Keys](#api-keys)
    - [Installation](#installation)
        - [From PyPi](#from-pypi)
        - [From Source](#from-source)
- [Usage](#usage)
    - [VirgoCXClient](#virgocxclient)
    - [Get KLine Data](#get-kline-data)
    - [Get Ticker Data](#get-ticker-data)
    - [Account Information](#account-information)
    - [Query Orders](#query-orders)
    - [Query Trades](#query-trades)
    - [Place Order](#place-order)
    - [Cancel Order](#cancel-order)
    - [Get Discount](#get-discount)
- [Warnings](#warnings)

## Setup

### API Keys

Generate your API key and secret from the [VirgoCX website](https://virgocx.ca/en-virgocx-api). Ensure
that the IP address of the machine you are running this client from is whitelisted.

### Installation

#### From PyPi

You can install this package from PyPi by running the following command in your terminal:

```bash
pip install vcx-py
```

#### From Source

After setting up your environment, install this package from source by running the following command in the
root directory of this project:

```bash
pip install . # Install the package to your environment
```

## Usage

### VirgoCXClient

Create a new instance of the `VirgoCXClient` class with your API key and secret.

```python
import vcx_py as vcx

vc = vcx.VirgoCXClient(api_key='your_api_key', api_secret='your_secret')
```

### Get KLine Data

Get KLine data for a specific trading pair.

```python
kline_data = vc.get_kline_data(symbol="BTC/CAD", period=vcx.Enums.KLineType.Minute)
```

### Get Ticker Data

Get ticker data for a specific trading pair.

```python
ticker_data = vc.get_ticker_data(symbol="BTC/CAD")
```

Or for all trading pairs.

```python
ticker_data = vc.tickers()
```

### Account Information

Get account information.

```python
account_info = vc.account_info()
```

This will give you information regarding your balances across all trading pairs.

### Query Orders

Retrieve your orders for a particular trading pair, optionally limited by order status.

```python
orders = vc.query_orders(symbol="BTC/CAD", status=vcx.Enums.OrderStatus.CANCELED)
```

### Query Trades

Retrieve trade (matching) information for a particular symbol.

```python
trades = vc.query_trades(symbol="BTC/CAD")
```

### Place Order

Place a new order.

```python
re = vc.place_order("USDC/CAD", vcx.Enums.OrderType.MARKET, vcx.Enums.OrderDirection.SELL, qty=30)
```

Note that on success, the response (a `dict`) will contain the order ID.

### Cancel Order

For a specified order ID, cancel the order.

```python
vc.cancel_order(order_id=12345)
```

### Get Discount

Returns similar output as `ticker` for a given symbol (or all symbols if one is not provided) with your account
discount applied to prices.

```python
discount = vc.get_discount(symbol="BTC/CAD")
```

## Warnings

Note that due to CloudFlare protection, this version of the client attempts to access the API through its
IP address and not the domain name. Should the IP address change, the client will need to be updated.
Moreover, you will receive `InsecureRequestWarning` warnings when using the client until this issue is resolved.
To suppress these warnings, you can use the following code:

```python
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

or you can use the environment variable `PYTHONWARNINGS` to suppress the warnings:

```bash
export PYTHONWARNINGS="ignore:Unverified HTTPS request"
```