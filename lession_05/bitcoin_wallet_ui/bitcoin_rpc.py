import re
from pathlib import Path
from urllib.parse import quote

import requests


# ==================================================
# CONFIGURATION
# ==================================================

RPC_URL = "http://127.0.0.1:18443"
COOKIE_PATH = Path.home() / ".bitcoin" / "regtest" / ".cookie"

MAX_BLOCKS_PER_CALL = 500

_WALLET_NAME = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")

# One HTTP session = one reused TCP connection (much faster when a page
# needs dozens of RPC calls, e.g. the block explorer).
_session = requests.Session()


# ==================================================
# CORE RPC CLIENT
# ==================================================

def rpc_call(method, params=None, wallet=None):
    """Execute a Bitcoin Core JSON-RPC request."""

    if not COOKIE_PATH.exists():
        raise RuntimeError(
            f"RPC cookie not found: {COOKIE_PATH}"
        )

    cookie = COOKIE_PATH.read_text().strip()

    try:
        username, password = cookie.split(":", 1)
    except ValueError:
        raise RuntimeError(
            "Bitcoin Core RPC cookie has an invalid format."
        )

    url = RPC_URL

    if wallet is not None:
        url += "/wallet/" + quote(wallet, safe="")

    payload = {
        "jsonrpc": "2.0",
        "id": "bitcoin-wallet-dashboard",
        "method": method,
        "params": params or [],
    }

    try:
        response = _session.post(
            url,
            json=payload,
            auth=(username, password),
            timeout=15,
        )
    except requests.RequestException as error:
        raise RuntimeError(
            f"Cannot reach Bitcoin Core at {RPC_URL}: {error}"
        ) from error

    # Bitcoin Core answers RPC errors with an HTTP error status *and* a JSON
    # body. Read the body first so the real message ("Insufficient funds",
    # "Fee estimation failed", ...) is shown instead of "500 Server Error".
    try:
        data = response.json()
    except ValueError:
        response.raise_for_status()
        raise RuntimeError(
            "Bitcoin Core returned a response that is not valid JSON."
        )

    if data.get("error") is not None:
        error = data["error"]
        raise RuntimeError(
            f"Bitcoin Core RPC error "
            f"{error.get('code')}: {error.get('message')}"
        )

    response.raise_for_status()

    return data["result"]


# ==================================================
# BLOCKCHAIN INFORMATION
# ==================================================

def get_blockchain_info():
    return rpc_call("getblockchaininfo")


def require_regtest():
    """Ensure wallet operations run only on regtest."""

    info = get_blockchain_info()

    if info.get("chain") != "regtest":
        raise RuntimeError(
            "Safety check failed: regtest network required."
        )

    return info


def get_connection_count():
    """Return the number of connected P2P peers."""

    return rpc_call("getconnectioncount")


def get_latest_block_hash():
    info = get_blockchain_info()

    if info["blocks"] == 0:
        return "No blocks mined yet"

    return rpc_call(
        "getblockhash",
        [info["blocks"]],
    )


# ==================================================
# BLOCK EXPLORER
# ==================================================

def get_block_hash(height):
    return rpc_call("getblockhash", [int(height)])


def get_block(block_hash, verbosity=1):
    """verbosity 1 = block header + txids, 2 = full decoded transactions."""

    return rpc_call("getblock", [block_hash, verbosity])


def get_block_by_height(height, verbosity=1):
    return get_block(get_block_hash(height), verbosity)


def get_recent_blocks(count=20, tip_height=None):
    """Return the latest blocks, newest first."""

    if count < 1:
        raise ValueError("Count must be positive.")

    if tip_height is None:
        tip_height = get_blockchain_info()["blocks"]

    first_height = max(tip_height - count + 1, 0)

    return [
        get_block_by_height(height)
        for height in range(tip_height, first_height - 1, -1)
    ]


# ==================================================
# NODE INFORMATION
# ==================================================

def get_network_info():
    return rpc_call("getnetworkinfo")


def get_mining_info():
    return rpc_call("getmininginfo")


def get_uptime():
    """Node uptime in seconds."""

    return rpc_call("uptime")


def get_peer_info():
    return rpc_call("getpeerinfo")


def get_chain_tips():
    return rpc_call("getchaintips")


# ==================================================
# WALLET MANAGEMENT
# ==================================================

def list_wallets():
    """Return currently loaded wallet names."""

    return rpc_call("listwallets")


def list_wallet_dir():
    """Return the names of all wallets on disk (loaded or not)."""

    result = rpc_call("listwalletdir")

    return [item["name"] for item in result.get("wallets", [])]


def create_wallet(name):
    """Create and load a new wallet."""

    require_regtest()

    name = (name or "").strip()

    if not _WALLET_NAME.match(name):
        raise ValueError(
            "Wallet names can only contain letters, digits, '_', '-' "
            "and '.' (1 to 64 characters)."
        )

    return rpc_call("createwallet", [name])


def load_wallet(name):
    """Load an existing wallet from disk."""

    require_regtest()

    return rpc_call("loadwallet", [name])


def get_wallet_info(wallet):
    return rpc_call("getwalletinfo", wallet=wallet)


def get_wallet_balances(wallet):
    """Return balance categories for a wallet."""

    return rpc_call(
        "getbalances",
        wallet=wallet,
    )


def get_new_address(wallet):
    """Generate a new receiving address."""

    return rpc_call(
        "getnewaddress",
        ["", "bech32"],
        wallet=wallet,
    )


def list_unspent(wallet, min_confirmations=0):
    """Return the wallet's spendable outputs (UTXOs)."""

    return rpc_call(
        "listunspent",
        [min_confirmations],
        wallet=wallet,
    )


# ==================================================
# SEND BITCOIN
# ==================================================

def send_to_address(wallet, address, amount, fee_rate=None):
    """Send regtest BTC from the selected wallet.

    fee_rate is optional and expressed in sat/vB. When omitted, Bitcoin Core
    picks the fee itself (which can fail on a fresh regtest chain because
    fee estimation has no data).
    """

    require_regtest()

    if not address or not address.strip():
        raise ValueError("Recipient address cannot be empty.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if amount > 21_000_000:
        raise ValueError("Amount exceeds the Bitcoin supply limit.")

    amount = round(amount, 8)

    if fee_rate is None:
        params = [address.strip(), amount]
    else:
        if fee_rate <= 0:
            raise ValueError("Fee rate must be greater than zero.")

        params = {
            "address": address.strip(),
            "amount": amount,
            "fee_rate": fee_rate,
        }

    return rpc_call(
        "sendtoaddress",
        params,
        wallet=wallet,
    )


# ==================================================
# MINING
# ==================================================

def mine_blocks(wallet, number_of_blocks):
    """Mine regtest blocks to an address belonging to the wallet."""

    require_regtest()

    if not isinstance(number_of_blocks, int):
        raise ValueError("Block count must be an integer.")

    if not 1 <= number_of_blocks <= MAX_BLOCKS_PER_CALL:
        raise ValueError(
            f"Choose between 1 and {MAX_BLOCKS_PER_CALL} blocks."
        )

    address = get_new_address(wallet)

    return rpc_call(
        "generatetoaddress",
        [number_of_blocks, address],
    )


# ==================================================
# MEMPOOL
# ==================================================

def get_mempool_info():
    """Return mempool size, usage, and other statistics."""

    return rpc_call("getmempoolinfo")


def get_mempool_transactions():
    """Return transaction IDs currently in the mempool."""

    return rpc_call("getrawmempool")


def get_mempool_entries():
    """Return {txid: details} (vsize, fees, time, ancestors...)."""

    return rpc_call("getrawmempool", [True])


# ==================================================
# TRANSACTION HISTORY
# ==================================================

def get_recent_transactions(wallet, count=20):
    """Return recent transactions known to the wallet (oldest first)."""

    if count < 1:
        raise ValueError("Count must be positive.")

    return rpc_call(
        "listtransactions",
        ["*", count],
        wallet=wallet,
    )


def get_transaction(wallet, txid, verbose=False):
    """Retrieve transaction details from a wallet.

    With verbose=True the result includes a "decoded" key with the inputs
    and outputs of the transaction.
    """

    if not txid or not txid.strip():
        raise ValueError("Transaction ID cannot be empty.")

    params = [txid.strip(), True, True] if verbose else [txid.strip()]

    return rpc_call(
        "gettransaction",
        params,
        wallet=wallet,
    )


# ==================================================
# CONNECTION TEST
# ==================================================

if __name__ == "__main__":
    try:
        info = get_blockchain_info()

        print("Network:", info["chain"])
        print("Block height:", info["blocks"])
        print("Peer connections:", get_connection_count())
        print("Loaded wallets:", list_wallets())

        print("\nMempool:")
        print("Transactions:", get_mempool_info()["size"])

    except Exception as error:
        print("RPC test failed:", error)