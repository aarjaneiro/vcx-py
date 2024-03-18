# VirgoCX Python Client

A simple Python client for the VirgoCX API.

For more information on the REST api on which this was built, please refer to the
[VirgoCX API Documentation](https://github.com/VirgocxDev/VirgocxApiDoc).

## Setup

### API Keys

Generate your API key and secret from the [VirgoCX website](https://virgocx.ca/en-virgocx-api). Ensure
that the IP address of the machine you are running this client from is whitelisted.

### Installation

After setting up your environment, install this package from source by running the following command in the
root directory of this project:

```bash
pip install . # Install the package to your environment
```

## Usage

As an example, you can use the following code to get your account information:

```python

from vcx_py import VirgoCXClient

vc = VirgoCXClient(api_key='your_api_key', api_secret='your_secret')
print(vc.account_info())
```

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