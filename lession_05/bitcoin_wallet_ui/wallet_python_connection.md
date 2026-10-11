Perfect! We found the answer. Your Bitcoin Core configuration has no RPC username or password configured, but your node has an authentication cookie:

```
/home/mohamed-amine/.bitcoin/regtest/.cookie
```

Bitcoin Core generated this cookie automatically. We can use it to authenticate your Python application without creating a username or password manually.

## Step 1 — Understand cookie authentication

Your configuration already contains:

```
regtest=1
server=1

[regtest]
rpcbind=127.0.0.1
rpcport=18443
rpcallowip=127.0.0.1
```

Your Python application will connect to `127.0.0.1:18443` and read the cookie to obtain its RPC credentials.

## Step 2 — Update `bitcoin_rpc.py`

Replace the previous version with this simpler implementation:

```
from pathlib import Path

import requests

RPC_URL = "http://127.0.0.1:18443"
COOKIE_PATH = Path.home() / ".bitcoin" / "regtest" / ".cookie"


def rpc_call(method, params=None, wallet=None):
    """Call Bitcoin Core using cookie authentication."""

    if not COOKIE_PATH.exists():
        raise RuntimeError(
            f"Bitcoin Core RPC cookie not found: {COOKIE_PATH}"
        )

    # Bitcoin Core cookie format: __cookie__:random_password
    cookie = COOKIE_PATH.read_text().strip()
    username, password = cookie.split(":", 1)

    url = RPC_URL

    if wallet:
        url += "/wallet/" + requests.utils.quote(wallet, safe="")

    payload = {
        "jsonrpc": "2.0",
        "id": "wallet-dashboard",
        "method": method,
        "params": params or [],
    }

    response = requests.post(
        url,
        json=payload,
        auth=(username, password),
        timeout=10,
    )

    response.raise_for_status()
    result = response.json()

    if result.get("error"):
        raise RuntimeError(str(result["error"]))

    return result["result"]


def get_blockchain_info():
    return rpc_call("getblockchaininfo")


def list_wallets():
    return rpc_call("listwallets")


if __name__ == "__main__":
    info = get_blockchain_info()

    print("Network:", info["chain"])
    print("Block height:", info["blocks"])
    print("Loaded wallets:", list_wallets())
```

Notice that we no longer need `RPC_USER`, `RPC_PASSWORD`, or environment variables.

The cookie is read automatically every time an RPC request is made. This also means the application can continue working if Bitcoin Core regenerates its cookie after a restart.

## Step 3 — Test the connection

From your project directory, activate your virtual environment:

```
cd ~/bitcoin-wallet-dashboard
source .venv/bin/activate
```

Ensure Requests is installed:

```
pip install requests
```

Run the Python client:

```
python bitcoin_rpc.py
```

Expected output will resemble:

```
Network: regtest
Block height: 101
Loaded wallets: ['Amine', 'Sara', 'Omar']
```

Your block height and wallet names may be different.

If you get `Connection refused`, Bitcoin Core may not be running. If you get `401 Unauthorized`, we should verify that the cookie belongs to the active node.

Security: Keep the cookie private. Anyone who can use it to authenticate to your local node may be able to control its wallets.

## What comes next?

Once this test succeeds, we'll build the first Streamlit screen:

- Select Amine, Sara, or Omar.
- Display the selected wallet's confirmed and unconfirmed balances.
- Refresh the displayed balances.

No transaction-sending functionality until the dashboard and wallet selection work correctly.

The difference is how your Python application authenticates itself to Bitcoin Core. The way it connects to the node stays almost the same.

There are two approaches: manually configured credentials and automatic cookie authentication.

## 1. The previous approach vs. the new approach

Previous approach — Username and password

```
RPC_USER = os.getenv("BITCOIN_RPC_USER")RPC_PASSWORD = os.getenv("BITCOIN_RPC_PASSWORD")
```

You must provide the username and password through environment variables, and Bitcoin Core must be configured to accept those credentials.

Manual configuration

New approach — Authentication cookie

```
cookie = COOKIE_PATH.read_text().strip()username, password = cookie.split(":", 1)
```

Bitcoin Core generates the cookie automatically. Python reads it from the existing `.cookie` file and uses its contents to authenticate.

Automatic credentials

## 2. How does cookie authentication work?

In your setup, Bitcoin Core created this file:

```
~/.bitcoin/regtest/.cookie
```

Inside, it contains a line in this format:

```
__cookie__:some_generated_secret
```

This is an example format, not your actual secret.

Here's what happens:

1\. Bitcoin Core starts

Generates the authentication cookie

2\. Python reads `.cookie`

Extracts the temporary credentials

3\. Python sends an RPC request

HTTP request to 127.0.0.1:18443

4\. Bitcoin Core verifies it

Returns the requested data if authorized

## 3. What actually changed?

| Element           | Before                  | Now                         |
| ----------------- | ----------------------- | --------------------------- |
| RPC host          | `127.0.0.1`             | `127.0.0.1`                 |
| RPC port          | `18443`                 | `18443`                     |
| Authentication    | Environment variables   | Cookie file                 |
| Credential setup  | You provide credentials | Bitcoin Core generates them |
| Python dependency | `requests`              | `requests`                  |
| Bitcoin network   | `regtest`               | `regtest`                   |

Important: Cookie authentication is not inherently a different or weaker security method. Bitcoin Core's automatically generated cookie is designed to provide local RPC authentication without requiring you to manage a static password.

Also, the cookie file is not your Bitcoin wallet's private key. It authenticates your application to the node; it does not directly hold your bitcoins.

## 4. Which approach should we use?

For your local Bitcoin learning project, I recommend cookie authentication because Bitcoin Core is already configured for it. You don't need to modify `bitcoin.conf` or invent credentials.

One detail to remember: your Python application runs under your Linux user, so it must be able to read the cookie file. If you restart Bitcoin Core, the cookie may change, which is why our code reads the file for each RPC call.

### Quick practice questions

1. Does changing authentication change the Bitcoin blockchain or wallet balances?
2. What does Bitcoin Core use the cookie for?
3. If Bitcoin Core restarts and generates a new cookie, why can our Python code still work without manually updating a password?


-----------------------------------------------------------
# How authentication works between Streamlit and Bitcoin Core

In your project, Streamlit is the web interface, Python is the client, and Bitcoin Core is the node that controls the wallets and processes transactions.

Your current setup uses Bitcoin Core's cookie authentication. Let's understand how it works, why we use it, and what other authentication methods exist.

## 1. Your current architecture

Browser

You interact with Streamlit

Streamlit — `app.py`

Displays balances, send forms, mining and mempool

Python RPC client — `bitcoin_rpc.py`

Reads the cookie and creates authenticated HTTP requests

Bitcoin Core 31.1

127.0.0.1:18443 · regtest

There are two distinct connections here:

- Browser → Streamlit: communicates with your web application.
- Python → Bitcoin Core: communicates through JSON-RPC and uses Bitcoin Core's RPC authentication.

The cookie authenticates the Python client to Bitcoin Core. It does not authenticate users who open the Streamlit webpage.

## 2. How your cookie authentication works

Your Bitcoin Core configuration includes:

```
regtest=1
server=1

[regtest]
rpcbind=127.0.0.1
rpcport=18443
rpcallowip=127.0.0.1
```

You did not configure `rpcuser` or `rpcpassword`. Instead, Bitcoin Core generated this file:

```
/home/mohamed-amine/.bitcoin/regtest/.cookie
```

The file contains a username and a randomly generated secret in a format similar to:

```
__cookie__:some_random_secret
```

That is an example, not your actual credential.

### Step-by-step authentication

1. Bitcoin Core starts. It generates an RPC authentication cookie and writes it to the regtest data directory.
2. Python reads the cookie. Your `bitcoin_rpc.py` reads the file and splits its contents into a username and password.
3. Python sends a request. For example, the app calls `getblockchaininfo` using HTTP POST and JSON-RPC.
4. HTTP authentication is attached. The Python `requests` library sends the cookie credentials using HTTP Basic Authentication.
5. Bitcoin Core checks the credentials. If they are valid and the connection is permitted, Bitcoin Core executes the RPC method and returns JSON.

Here is the relevant part of your Python code:

```
cookie = COOKIE_PATH.read_text().strip()username, password = cookie.split(":", 1)response = requests.post(    RPC_URL,    json=payload,    auth=(username, password),    timeout=15,)
```

The argument `auth=(username, password)` tells `requests` to use HTTP Basic Authentication. It does not implement the authentication algorithm itself; the library handles the HTTP header.

## 3. What happens inside the HTTP request?

Suppose your Python app wants to retrieve the blockchain information.

It sends a request conceptually like this:

```
POST / HTTP/1.1
Host: 127.0.0.1:18443
Content-Type: application/json
Authorization: Basic <encoded-credentials>

{
  "jsonrpc": "2.0",
  "id": "dashboard",
  "method": "getblockchaininfo",
  "params": []
}
```

The `Authorization` header contains the username and password encoded using Base64.

Important: Base64 is encoding, not encryption. Anyone who intercepts an ordinary HTTP request can potentially recover the credentials. Your current setup limits RPC to localhost, which reduces exposure. For remote connections, use a properly secured connection such as a VPN or SSH tunnel rather than exposing plain HTTP RPC to the internet.

Bitcoin Core then returns a response resembling:

```
{
  "result": {
    "chain": "regtest",
    "blocks": 103
  },
  "error": null,
  "id": "dashboard"
}
```

This is an illustrative partial response. Your actual response contains additional fields.

Notice that authentication and authorization are different concepts:

- Authentication: Are the supplied RPC credentials valid?
- Authorization: Is the authenticated client allowed to access the requested operation under the node's configuration and permissions?

Bitcoin Core's RPC credentials generally grant access to powerful node and wallet operations; the cookie is not a separate read-only dashboard credential.

## 4. Different types of Bitcoin Core RPC authentication

There are three main configurations worth understanding.

### Type 1 — Cookie authentication

Your setup

How it works: Bitcoin Core generates a temporary credential automatically, and a local client reads the cookie file.

Example:

```
~/.bitcoin/regtest/.cookie
```

Advantages

- No manual password configuration.
- Credentials can be regenerated when the node restarts.
- Suitable for local applications and command-line tools.

Limitations

- The client needs permission to read the cookie.
- Anyone who obtains a valid cookie may gain RPC access.
- The client must handle cookie rotation correctly.

### Type 2 — Static username and password

How it works: An administrator configures an RPC username and password, and the client supplies those credentials.

A legacy-style example is:

```
rpcuser=dashboard
rpcpassword=use_a_long_random_secret
```

Advantages

- Easy to understand.
- The credentials can remain stable across restarts.

Limitations

- You must manage and protect the password.
- A password stored in a configuration file needs appropriate file permissions.
- Legacy `rpcuser`/`rpcpassword` configuration is generally less desirable than cookie authentication or `rpcauth`.

For your learning dashboard, you do not need to switch to this method.

### Type 3 — `rpcauth`

How it works: Bitcoin Core is configured with an RPC username and a salted password verifier. The client still sends the actual password through the RPC HTTP authentication mechanism.

An illustrative configuration entry looks like:

```
rpcauth=dashboard:<salt>$<password_hmac>
```

The placeholders are not usable credentials.

Advantages

- The server configuration stores a verifier rather than the plaintext RPC password.
- Useful when you need a configured RPC account instead of automatic cookie authentication.

Limitations

- Requires generating the verifier and securely provisioning the client's password.
- It is still not a substitute for network security or encrypted transport.

This is useful to learn about when you eventually separate your dashboard and Bitcoin Core onto different machines.

These are RPC authentication methods, not Bitcoin wallet signing methods. Your wallet's private keys and transaction signatures are separate from the credentials that let Python call the node.

## 5. What about other authentication methods?

Some related security mechanisms are often confused with Bitcoin Core RPC authentication.

| Mechanism                 | Purpose                                                                            | Used in your app?                                     |
| ------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------- |
| HTTP Basic Authentication | Sends RPC credentials in an HTTP header                                            | Yes                                                   |
| Cookie authentication     | Provides automatically generated RPC credentials                                   | Yes                                                   |
| `rpcauth`                 | Configures an RPC username and password verifier                                   | No                                                    |
| TLS / HTTPS               | Encrypts network traffic and authenticates endpoints when configured appropriately | No; current RPC URL is HTTP                           |
| SSH tunnel / VPN          | Protects and restricts remote network access                                       | No; unnecessary for your current localhost connection |
| Wallet private key        | Authorizes Bitcoin spending by signing transactions                                | Bitcoin Core manages this separately                  |

A particularly important distinction: HTTP Basic Authentication is the transport-level authentication mechanism; cookie authentication is how Bitcoin Core supplies the credentials. They are not competing methods in your implementation.

## 6. Why doesn't the cookie authenticate users of your website?

Imagine someone opens your Streamlit dashboard in a browser.

The browser does not need to know the RPC cookie. Instead, `app.py` calls `bitcoin_rpc.py`, and that Python process reads the cookie on the server.

This means everyone who can use your dashboard may indirectly be able to request operations using the application's RPC privileges. Since your app supports sending bitcoin and mining, keep it local and do not expose it to an untrusted network.

For your current lab, the configuration is appropriate:

- Bitcoin Core listens for RPC on `127.0.0.1`.
- Python reads the cookie locally.
- The app verifies that the node is on `regtest` before sending or mining.
- Bitcoin Core handles wallet keys and transaction signing.

One subtlety: the regtest check is an application-level safeguard, not a complete security boundary. It is important to keep the RPC endpoint and cookie protected as well.

## 7. A small experiment to understand the authentication

You can observe the distinction between credentials and RPC methods without exposing the cookie.

First, check the cookie's permissions:

```
stat -c '%a %U %n' ~/.bitcoin/regtest/.cookie
```

Then check that your existing client can authenticate:

```
python bitcoin_rpc.py
```

Finally, try an invalid RPC method in a temporary test:

```
print(rpc_call("method_that_does_not_exist"))
```

With valid credentials, Bitcoin Core should respond with an RPC error for the unknown method. That differs from an HTTP authentication failure such as `401 Unauthorized`.

## Practice questions

1. Why does your application use both a cookie file and HTTP Basic Authentication?
2. Why is Base64 encoding not sufficient to protect credentials over an untrusted network?
3. If a person can open your Streamlit dashboard, does that automatically mean they can read the RPC cookie file directly? What indirect access might they still have?
4. What is the difference between an RPC authentication credential and a wallet's private key?

![Alt Text](/lession_05/bitcoin_wallet_ui/images/Screenshot%20from%202026-10-11%2014-17-53.png)
![Alt Text](/lession_05/bitcoin_wallet_ui/images/Screenshot%20from%202026-10-11%2014-17-59.png)
![Alt Text](/lession_05/bitcoin_wallet_ui/images/Screenshot%20from%202026-10-11%2014-18-05.png)
![Alt Text](/lession_05/bitcoin_wallet_ui/images/Screenshot%20from%202026-10-11%2014-18-08.png)
![Alt Text](/lession_05/bitcoin_wallet_ui/images/Screenshot%20from%202026-10-11%2014-18-11.png)
![Alt Text](/lession_05/bitcoin_wallet_ui/images/Screenshot%20from%202026-10-11%2014-18-15.png)