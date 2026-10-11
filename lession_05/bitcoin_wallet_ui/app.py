import html
import io
import time
from datetime import datetime

import pandas as pd
import streamlit as st

from bitcoin_rpc import (
    MAX_BLOCKS_PER_CALL,
    list_wallets,
    list_wallet_dir,
    create_wallet,
    load_wallet,
    get_wallet_balances,
    get_wallet_info,
    get_blockchain_info,
    get_connection_count,
    get_latest_block_hash,
    get_new_address,
    list_unspent,
    send_to_address,
    mine_blocks,
    get_mempool_info,
    get_mempool_entries,
    get_recent_blocks,
    get_block_by_height,
    get_recent_transactions,
    get_transaction,
    get_network_info,
    get_mining_info,
    get_uptime,
    get_peer_info,
    get_chain_tips,
)

try:  # optional: pip install "qrcode[pil]"
    import qrcode
except ImportError:
    qrcode = None


# ==================================================
# SETTINGS
# ==================================================

AMBER = "#f7931a"
BLOCK_WINDOW = 60      # blocks fetched for charts and the block explorer
TX_WINDOW = 1000       # wallet transactions fetched for history and charts


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Bitcoin Regtest Control Center",
    page_icon="₿",
    layout="wide",
)


# ==================================================
# STYLE
# ==================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
:root{--ink:#0c1517;--panel:#111d20;--line:#22343a;--text:#e9eef0;--muted:#86999f;--amber:#f7931a;--amber-soft:#ffc46b;--ok:#5fd0a0;--mono:'IBM Plex Mono',ui-monospace,monospace;}
html,body,.stApp{font-family:'IBM Plex Sans',system-ui,sans-serif;background:var(--ink);color:var(--text);}
header[data-testid="stHeader"]{background:transparent;}
#MainMenu,footer{visibility:hidden;}
.block-container{max-width:1180px;padding-top:2.2rem;padding-bottom:3rem;}
[data-testid="stSidebar"]{background:var(--panel);border-right:1px solid var(--line);}
[data-testid="stSidebar"] .stButton>button{width:100%;}

.app-head{display:flex;align-items:flex-end;justify-content:space-between;gap:1rem;border-bottom:1px solid var(--line);padding-bottom:1.1rem;margin-bottom:1.2rem;}
.app-title{font-size:1.7rem;font-weight:600;letter-spacing:-.01em;margin:0;line-height:1.2;}
.app-title .btc{color:var(--amber);margin-right:.4rem;}
.app-sub{color:var(--muted);font-size:.92rem;margin-top:.25rem;}
.pill{display:inline-flex;align-items:center;gap:.5rem;font-family:var(--mono);font-size:.78rem;padding:.28rem .7rem;border-radius:999px;border:1px solid var(--line);color:var(--text);white-space:nowrap;}
.pill .dot{width:7px;height:7px;border-radius:50%;background:var(--ok);}

.brand{font-size:1.05rem;font-weight:600;margin-bottom:.9rem;}
.brand .btc{color:var(--amber);margin-right:.35rem;}

.sec-title{font-size:1.2rem;font-weight:600;margin:.4rem 0 .15rem;}
.sec-sub{color:var(--muted);font-size:.92rem;margin-bottom:1rem;}
.chart-title{font-size:.95rem;font-weight:600;margin:.2rem 0 .5rem;}
.note{color:var(--muted);font-size:.85rem;line-height:1.55;margin-top:.8rem;}
.gap{height:1rem;}

.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1.1rem 1.3rem;}
.panel-title{font-size:.95rem;font-weight:600;margin-bottom:.5rem;}

.balance{padding:1.5rem 1.7rem;border:1px solid var(--line);border-left:3px solid var(--amber);border-radius:10px;background:var(--panel);}
.balance-label{color:var(--muted);font-size:.92rem;}
.balance-amt{font-family:var(--mono);font-size:2.9rem;font-weight:500;line-height:1.15;margin:.3rem 0 1.1rem;letter-spacing:-.02em;}
.amt{color:var(--text);}
.amt .dim{color:#4b5f66;}
.unit{font-size:1rem;color:var(--amber);margin-left:.7rem;letter-spacing:0;}
.balance-split{display:flex;flex-wrap:wrap;gap:.8rem 2.8rem;border-top:1px solid var(--line);padding-top:.95rem;}
.balance-split .k{display:block;color:var(--muted);font-size:.82rem;margin-bottom:.1rem;}
.balance-split .v{font-family:var(--mono);font-size:1.05rem;}

.ledger .row{display:flex;align-items:baseline;gap:.55rem;padding:.4rem 0;}
.ledger .k{color:var(--muted);font-size:.9rem;white-space:nowrap;}
.ledger .dots{flex:1;border-bottom:1px dotted #33484f;transform:translateY(-3px);}
.ledger .v{font-family:var(--mono);font-size:.92rem;text-align:right;word-break:break-all;}

.stat{padding:.15rem 0 .15rem 1rem;border-left:2px solid var(--amber);}
.stat-v{font-family:var(--mono);font-size:1.6rem;font-weight:500;}
.stat-k{color:var(--muted);font-size:.86rem;}

.stTabs [data-baseweb="tab-list"]{gap:1.6rem;border-bottom:1px solid var(--line);overflow-x:auto;}
.stTabs [data-baseweb="tab"]{height:auto;padding:.65rem 0;background:transparent;color:var(--muted);font-weight:500;}
.stTabs [aria-selected="true"]{color:var(--text);}
.stTabs [data-baseweb="tab-highlight"]{background:var(--amber);height:2px;}
.stTabs [data-baseweb="tab-border"]{background:transparent;}

.stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{border-radius:8px;font-weight:600;border:1px solid var(--line);background:transparent;color:var(--text);}
.stButton>button:hover,.stFormSubmitButton>button:hover,.stDownloadButton>button:hover{border-color:var(--amber);color:var(--amber-soft);}
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-primaryFormSubmit"],.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primaryFormSubmit"]{background:var(--amber);border-color:var(--amber);color:#1b1205;}
[data-testid="stBaseButton-primary"]:hover,[data-testid="stBaseButton-primaryFormSubmit"]:hover,.stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primaryFormSubmit"]:hover{background:var(--amber-soft);border-color:var(--amber-soft);color:#1b1205;}

[data-testid="stForm"]{border:1px solid var(--line);border-radius:10px;background:var(--panel);padding:1.2rem 1.3rem;}
[data-testid="stExpander"]{border-color:var(--line);border-radius:10px;}
.stCode,[data-testid="stCode"]{border-radius:8px;}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ==================================================
# UI HELPERS
# ==================================================

def esc(value):
    return html.escape(str(value))


def btc_html(value):
    """Render a BTC amount with the trailing zeros dimmed."""
    text = f"{float(value):.8f}"
    head = text.rstrip("0")
    if head.endswith("."):
        head += "0"
    tail = text[len(head):]
    return f'<span class="amt">{head}<span class="dim">{tail}</span></span>'


def short(value, edge=8):
    value = str(value)
    if len(value) <= edge * 2 + 1:
        return value
    return f"{value[:edge]}…{value[-edge:]}"


def fmt_time(epoch):
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def fmt_duration(seconds):
    seconds = int(max(seconds, 0))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def fmt_bytes(size):
    size = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:,.0f} {unit}" if unit == "B" else f"{size:,.1f} {unit}"
        size /= 1024


def section(title, subtitle=""):
    sub = f'<div class="sec-sub">{esc(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="sec-title">{esc(title)}</div>{sub}',
        unsafe_allow_html=True,
    )


def chart_title(title):
    st.markdown(
        f'<div class="chart-title">{esc(title)}</div>',
        unsafe_allow_html=True,
    )


def gap():
    st.markdown('<div class="gap"></div>', unsafe_allow_html=True)


def ledger_html(rows):
    body = "".join(
        f'<div class="row"><span class="k">{esc(k)}</span>'
        f'<span class="dots"></span><span class="v">{esc(v)}</span></div>'
        for k, v in rows
    )
    return f'<div class="ledger">{body}</div>'


def panel(title, rows, note=""):
    note_html = f'<div class="note">{esc(note)}</div>' if note else ""
    st.markdown(
        f'<div class="panel"><div class="panel-title">{esc(title)}</div>'
        f"{ledger_html(rows)}{note_html}</div>",
        unsafe_allow_html=True,
    )


def stat(column, value, label):
    column.markdown(
        f'<div class="stat"><div class="stat-v">{esc(value)}</div>'
        f'<div class="stat-k">{esc(label)}</div></div>',
        unsafe_allow_html=True,
    )


def show_table(data):
    try:
        st.dataframe(data, hide_index=True, width="stretch")
    except Exception:  # older Streamlit versions
        st.dataframe(data, hide_index=True, use_container_width=True)


def qr_png(data):
    image = qrcode.make(data)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def set_flash(tab, kind, message, code=None):
    """Keep a message across st.rerun() so it shows after the refresh."""
    st.session_state[f"flash_{tab}"] = {
        "kind": kind,
        "message": message,
        "code": code,
    }


def show_flash(tab):
    item = st.session_state.pop(f"flash_{tab}", None)

    if item:
        getattr(st, item["kind"])(item["message"])

        if item.get("code"):
            st.code(item["code"], language=None)


# ==================================================
# DATA HELPERS
# ==================================================

@st.cache_data(ttl=15, show_spinner=False)
def fetch_blocks(tip_hash, count):
    """Cached per chain tip: a new block changes tip_hash and refreshes it."""
    return get_recent_blocks(count)


def blocks_dataframe(blocks):
    """Blocks (newest first from RPC) -> DataFrame sorted by height."""
    if not blocks:
        return pd.DataFrame()

    df = pd.DataFrame(
        [
            {
                "Height": block["height"],
                "Hash": block["hash"],
                "Epoch": block["time"],
                "Txs": block["nTx"],
                "Size (B)": block["size"],
                "Weight": block["weight"],
            }
            for block in blocks
        ]
    )

    df = df.sort_values("Height").reset_index(drop=True)
    df["Time"] = df["Epoch"].apply(datetime.fromtimestamp)
    df["Interval (s)"] = df["Epoch"].diff()

    return df


def history_dataframe(transactions):
    """listtransactions output -> DataFrame (oldest first)."""
    if not transactions:
        return pd.DataFrame()

    df = pd.DataFrame(
        [
            {
                "Time": datetime.fromtimestamp(tx.get("time", 0)),
                "Category": tx.get("category", ""),
                "Address": tx.get("address", ""),
                "Amount": float(tx.get("amount", 0)),
                "Fee": float(tx.get("fee", 0) or 0),
                "Confirmations": tx.get("confirmations", 0),
                "Txid": tx.get("txid", ""),
            }
            for tx in transactions
        ]
    )

    # The fee is repeated on every "send" row of the same transaction.
    repeated = df.duplicated(subset=["Txid", "Category"])
    df.loc[repeated, "Fee"] = 0.0

    return df


def balance_history(df):
    """Cumulative wallet balance, one point per transaction."""
    if df.empty:
        return pd.Series(dtype=float)

    counted = df[~df["Category"].isin(["immature", "orphan"])]
    series = (counted["Amount"] + counted["Fee"]).cumsum().reset_index(drop=True)
    series.index = range(1, len(series) + 1)

    return series


def wallet_summaries(names):
    rows, errors = [], []

    for name in names:
        try:
            mine = get_wallet_balances(name)["mine"]
            tx_count = get_wallet_info(name).get("txcount", 0)
        except Exception as error:
            errors.append(f'Wallet {name or "(default wallet)"}: {error}')
            continue

        rows.append(
            {
                "Wallet": name or "(default wallet)",
                "Confirmed": mine["trusted"],
                "Unconfirmed": mine["untrusted_pending"],
                "Immature": mine["immature"],
                "Total": mine["trusted"]
                + mine["untrusted_pending"]
                + mine["immature"],
                "Transactions": tx_count,
            }
        )

    return rows, errors


load_errors = []


def load(label, function, default, *args, **kwargs):
    """Fetch secondary dashboard data without breaking the whole page."""
    try:
        return function(*args, **kwargs)
    except Exception as error:
        load_errors.append(f"{label}: {error}")
        return default


def render_transaction(details):
    decoded = details.get("decoded", {})

    panel(
        "Summary",
        [
            ("Confirmations", details.get("confirmations", 0)),
            ("Block height", details.get("blockheight", "unconfirmed")),
            ("Wallet amount", f'{details.get("amount", 0):.8f} BTC'),
            (
                "Fee",
                f'{details["fee"]:.8f} BTC' if "fee" in details else "—",
            ),
            (
                "Time",
                fmt_time(details["time"]) if "time" in details else "—",
            ),
            ("Size", f'{decoded.get("vsize", "—")} vB'),
        ],
    )

    gap()
    in_col, out_col = st.columns(2, gap="large")

    with in_col:
        chart_title("Inputs")
        inputs = [
            {
                "Source": "coinbase (new coins)"
                if "coinbase" in vin
                else f'{short(vin.get("txid", ""))}:{vin.get("vout", "")}'
            }
            for vin in decoded.get("vin", [])
        ]

        if inputs:
            show_table(inputs)
        else:
            st.caption("No decoded inputs.")

    with out_col:
        chart_title("Outputs")
        outputs = [
            {
                "#": vout.get("n"),
                "Amount (BTC)": vout.get("value"),
                "Address": vout.get("scriptPubKey", {}).get("address", "—"),
                "Type": vout.get("scriptPubKey", {}).get("type", "—"),
            }
            for vout in decoded.get("vout", [])
        ]

        if outputs:
            show_table(outputs)
        else:
            st.caption("No decoded outputs.")

    with st.expander("Raw JSON"):
        st.json(details)


# ==================================================
# SIDEBAR (brand + refresh)
# ==================================================

refresh_seconds = 10

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="btc">₿</span>Regtest lab</div>',
        unsafe_allow_html=True,
    )

    if st.button("Refresh dashboard"):
        st.rerun()

    auto_refresh = st.checkbox("Auto-refresh", value=False)

    if auto_refresh:
        refresh_seconds = st.select_slider(
            "Every",
            options=[5, 10, 30, 60],
            value=10,
            format_func=lambda seconds: f"{seconds}s",
        )


# ==================================================
# CONNECT TO BITCOIN CORE
# ==================================================

try:
    blockchain = get_blockchain_info()

    if blockchain.get("chain") != "regtest":
        st.error(
            "Safety check failed: this dashboard only supports regtest. "
            "Start Bitcoin Core with -regtest and reload."
        )
        st.stop()

    wallets = list_wallets()
    peer_count = get_connection_count()

except Exception as error:
    st.error(
        f"Cannot connect to Bitcoin Core: {error}. "
        "Check that bitcoind is running and the RPC settings are correct."
    )
    st.stop()


# ==================================================
# SIDEBAR (node + wallet)
# ==================================================

with st.sidebar:
    st.markdown(
        '<span class="pill"><span class="dot"></span>Connected · regtest</span>',
        unsafe_allow_html=True,
    )
    gap()

    st.markdown(
        ledger_html(
            [
                ("Block height", f'{blockchain["blocks"]:,}'),
                ("Peers", peer_count),
                ("RPC", "127.0.0.1:18443"),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.divider()

    if wallets:
        wallet = st.selectbox(
            "Wallet",
            wallets,
            format_func=lambda name: name or "(default wallet)",
        )
    else:
        wallet = None
        st.warning("No wallets are loaded.")

    st.divider()
    st.caption(f"Updated {datetime.now():%H:%M:%S}")
    st.caption("Local lab only. Regtest coins have no value.")


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="app-head"><div>'
    '<div class="app-title"><span class="btc">₿</span>Bitcoin Regtest Control Center</div>'
    '<div class="app-sub">Bitcoin Core 31.1 · local regtest learning dashboard</div>'
    "</div>"
    f'<span class="pill"><span class="dot"></span>block {blockchain["blocks"]:,}</span>'
    "</div>",
    unsafe_allow_html=True,
)

if wallet is None:
    st.info(
        "Load or create a wallet in Bitcoin Core "
        "(for example: bitcoin-cli -regtest createwallet lab), then refresh."
    )
    st.stop()

wallet_label = wallet or "(default wallet)"


# ==================================================
# WALLET BALANCES
# ==================================================

try:
    balance_data = get_wallet_balances(wallet)
    balances = balance_data["mine"]

except Exception as error:
    st.error(f"Could not retrieve wallet balances: {error}")
    st.stop()


# ==================================================
# DASHBOARD DATA
# ==================================================

mempool_info = load("Mempool", get_mempool_info, {})
mempool_entries = load("Mempool entries", get_mempool_entries, {})
utxos = load("Unspent outputs", list_unspent, [], wallet)
raw_transactions = load(
    "Transactions", get_recent_transactions, [], wallet, TX_WINDOW
)
recent_blocks = load(
    "Blocks", fetch_blocks, [], blockchain["bestblockhash"], BLOCK_WINDOW
)
summary_rows, summary_errors = wallet_summaries(wallets)
load_errors.extend(summary_errors)

blocks_df = blocks_dataframe(recent_blocks)
history_df = history_dataframe(raw_transactions)

if load_errors:
    with st.expander(f"{len(load_errors)} data source(s) could not be loaded"):
        for message in load_errors:
            st.write(message)


# ==================================================
# NAVIGATION
# ==================================================

(
    overview_tab,
    send_tab,
    receive_tab,
    mining_tab,
    mempool_tab,
    blocks_tab,
    wallets_tab,
    history_tab,
    node_tab,
) = st.tabs(
    [
        "Overview",
        "Send",
        "Receive",
        "Mining",
        "Mempool",
        "Blocks",
        "Wallets",
        "Transactions",
        "Node",
    ]
)


# ==================================================
# OVERVIEW
# ==================================================

with overview_tab:
    gap()
    section(wallet_label, "Balances and activity for the selected wallet.")

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown(
            '<div class="balance">'
            '<div class="balance-label">Confirmed balance</div>'
            f'<div class="balance-amt">{btc_html(balances["trusted"])}'
            '<span class="unit">BTC</span></div>'
            '<div class="balance-split">'
            f'<div><span class="k">Unconfirmed</span>'
            f'<span class="v">{btc_html(balances["untrusted_pending"])} BTC</span></div>'
            f'<div><span class="k">Immature mining rewards</span>'
            f'<span class="v">{btc_html(balances["immature"])} BTC</span></div>'
            "</div></div>",
            unsafe_allow_html=True,
        )

        gap()
        st.markdown("**Latest block hash**")

        try:
            st.code(get_latest_block_hash(), language=None)
        except Exception as error:
            st.warning(f"Could not retrieve the latest block hash: {error}")

    with right:
        panel(
            "Blockchain",
            [
                ("Network", blockchain["chain"]),
                ("Block height", f'{blockchain["blocks"]:,}'),
                ("Difficulty", f'{blockchain["difficulty"]:.8f}'),
                ("Peers", peer_count),
            ],
            note="Turn on Auto-refresh in the sidebar to follow the chain live.",
        )

    gap()

    total_all = sum(row["Total"] for row in summary_rows)
    last_block_age = (
        fmt_duration(time.time() - recent_blocks[0]["time"])
        if recent_blocks
        else "—"
    )

    k1, k2, k3, k4 = st.columns(4)
    stat(k1, f"{total_all:,.2f}", "BTC across loaded wallets")
    stat(k2, len(utxos), "Spendable outputs (UTXOs)")
    stat(k3, mempool_info.get("size", 0), "Transactions in mempool")
    stat(k4, last_block_age, "Since the last block")

    gap()

    chart_left, chart_right = st.columns(2, gap="large")

    with chart_left:
        chart_title("Transactions per block (last 30)")

        if blocks_df.empty:
            st.caption("No blocks yet.")
        else:
            st.bar_chart(
                blocks_df.tail(30).set_index("Height")["Txs"],
                color=AMBER,
                height=230,
            )

    with chart_right:
        chart_title("Wallet balance history (per transaction)")

        history_series = balance_history(history_df)

        if history_series.empty:
            st.caption("No transactions in this wallet yet.")
        else:
            st.area_chart(history_series, color=AMBER, height=230)


# ==================================================
# SEND BTC
# ==================================================

with send_tab:
    gap()
    section("Send test bitcoin", f"From wallet {wallet_label}.")
    show_flash("send")

    other_wallets = [name for name in wallets if name != wallet]

    option_left, option_right = st.columns(2)

    with option_left:
        destination_mode = st.radio(
            "Send to",
            ["Address", "Another loaded wallet"],
            horizontal=True,
        )

    with option_right:
        use_custom_fee = st.checkbox(
            "Set a custom fee rate",
            help="Needed when Bitcoin Core cannot estimate a fee "
            "on a fresh regtest chain.",
        )

    form_col, info_col = st.columns([3, 2], gap="large")

    with form_col:
        with st.form("send_form"):
            recipient_address = ""
            target_wallet = None

            if destination_mode == "Address":
                recipient_address = st.text_input(
                    "Recipient address",
                    placeholder="bcrt1…",
                )
            elif other_wallets:
                target_wallet = st.selectbox(
                    "Recipient wallet",
                    other_wallets,
                    format_func=lambda name: name or "(default wallet)",
                )
            else:
                st.info(
                    "Only one wallet is loaded. Create or load a second one "
                    "in the Wallets tab."
                )

            amount = st.number_input(
                "Amount (BTC)",
                min_value=0.00000001,
                max_value=21000000.0,
                value=0.1,
                step=0.1,
                format="%.8f",
            )

            fee_rate = None

            if use_custom_fee:
                fee_rate = st.number_input(
                    "Fee rate (sat/vB)",
                    min_value=1.0,
                    max_value=10000.0,
                    value=2.0,
                    step=0.5,
                )

            confirm_send = st.checkbox(
                "This is a test transaction on regtest."
            )

            send_submitted = st.form_submit_button(
                "Send bitcoin",
                type="primary",
            )

    with info_col:
        panel(
            "Before you send",
            [
                ("Spendable now", f'{balances["trusted"]:.8f} BTC'),
                ("Spendable outputs", len(utxos)),
                ("Wallet", wallet_label),
                ("Network", "regtest"),
            ],
            note="Check the address and amount first. A transaction stays "
            "unconfirmed until a block includes it.",
        )

    if send_submitted:
        destination = None
        txid = None

        if destination_mode == "Address":
            destination = recipient_address.strip()

            if not destination:
                st.error("Enter a recipient address.")

        elif target_wallet is None:
            st.error("No other wallet is loaded.")

        if not confirm_send:
            st.error("Tick the confirmation box to send.")

        elif destination_mode != "Address" and target_wallet is not None:
            try:
                destination = get_new_address(target_wallet)
            except Exception as error:
                destination = None
                st.error(f"Could not get an address from the wallet: {error}")

        if confirm_send and destination:
            try:
                txid = send_to_address(
                    wallet,
                    destination,
                    amount,
                    fee_rate if use_custom_fee else None,
                )
            except Exception as error:
                st.error(f"Transaction failed: {error}")

                if "fee" in str(error).lower() and not use_custom_fee:
                    st.caption(
                        "Tip: tick “Set a custom fee rate” above and try again."
                    )

        if txid:
            set_flash(
                "send",
                "success",
                "Transaction sent. It stays unconfirmed until a block "
                "includes it. Transaction ID:",
                code=txid,
            )
            st.rerun()


# ==================================================
# RECEIVE BTC
# ==================================================

with receive_tab:
    gap()
    section("Receive test bitcoin", f"Into wallet {wallet_label}.")

    if st.button("New receiving address", type="primary"):
        try:
            address = get_new_address(wallet)

            st.session_state["receiving_address"] = address
            st.session_state["receiving_wallet"] = wallet

        except Exception as error:
            st.error(f"Could not generate an address: {error}")

    address = st.session_state.get("receiving_address")
    address_wallet = st.session_state.get("receiving_wallet")

    if address and address_wallet == wallet:
        gap()
        addr_col, qr_col = st.columns([3, 2], gap="large")

        with addr_col:
            st.markdown("**Receiving address**")
            st.code(address, language=None)
            st.caption("This address belongs to the selected wallet.")

        with qr_col:
            if qrcode is not None:
                try:
                    st.image(qr_png(address), width=190)
                except Exception:
                    pass
    else:
        st.caption("Generate an address to start receiving coins.")


# ==================================================
# MINING
# ==================================================

def run_mining(block_total):
    try:
        with st.spinner("Mining…"):
            hashes = mine_blocks(wallet, int(block_total))
    except Exception as error:
        st.error(f"Mining failed: {error}")
        return

    set_flash(
        "mining",
        "success",
        f"Mined {len(hashes)} block(s). Latest block hash:",
        code=hashes[-1] if hashes else None,
    )
    st.rerun()


with mining_tab:
    gap()
    section("Mine regtest blocks", f"Rewards go to {wallet_label}.")
    show_flash("mining")

    chart_title("Quick actions")
    q1, q2, q3 = st.columns(3)

    if q1.button("Mine 1 block"):
        run_mining(1)

    if q2.button("Mine 10 blocks"):
        run_mining(10)

    if q3.button("Mine 101 blocks (unlock first reward)"):
        run_mining(101)

    gap()

    form_col, info_col = st.columns([3, 2], gap="large")

    with form_col:
        with st.form("mining_form"):
            block_count = st.number_input(
                "Number of blocks",
                min_value=1,
                max_value=MAX_BLOCKS_PER_CALL,
                value=1,
                step=1,
            )

            confirm_mining = st.checkbox(
                "Mine these blocks on my local regtest chain."
            )

            mine_submitted = st.form_submit_button(
                "Mine blocks",
                type="primary",
            )

    with info_col:
        panel(
            "Mining rules",
            [
                ("Reward wallet", wallet_label),
                ("Chain height", f'{blockchain["blocks"]:,}'),
                ("Reward maturity", "100 blocks"),
                ("Immature now", f'{balances["immature"]:.8f} BTC'),
            ],
            note="A coinbase reward is spendable after 100 confirmations. "
            "On a fresh chain, mine 101 blocks to unlock the first reward.",
        )

    if mine_submitted:
        if not confirm_mining:
            st.error("Tick the confirmation box to mine.")
        else:
            run_mining(block_count)


# ==================================================
# MEMPOOL
# ==================================================

with mempool_tab:
    gap()
    section(
        "Mempool",
        "Unconfirmed transactions waiting to be included in a block.",
    )

    if not mempool_info:
        st.error("Could not retrieve mempool information.")
    else:
        rows = []
        now = time.time()

        if isinstance(mempool_entries, dict):
            for txid, entry in mempool_entries.items():
                base_fee = float(entry.get("fees", {}).get("base", 0))
                vsize = entry.get("vsize") or 1

                rows.append(
                    {
                        "Transaction ID": txid,
                        "vsize (vB)": vsize,
                        "Fee (BTC)": base_fee,
                        "Fee rate (sat/vB)": round(base_fee * 1e8 / vsize, 2),
                        "Age (s)": int(now - entry.get("time", now)),
                        "Ancestors": entry.get("ancestorcount", 1),
                    }
                )

        mempool_df = pd.DataFrame(rows)

        total_fees = mempool_info.get(
            "total_fee",
            mempool_df["Fee (BTC)"].sum() if not mempool_df.empty else 0,
        )
        average_rate = (
            f'{mempool_df["Fee rate (sat/vB)"].mean():.1f}'
            if not mempool_df.empty
            else "—"
        )

        m1, m2, m3, m4 = st.columns(4)
        stat(m1, f'{mempool_info["size"]:,}', "Transactions")
        stat(m2, f'{mempool_info["bytes"]:,} B', "Virtual size")
        stat(m3, f"{total_fees:.6f}", "Total fees (BTC)")
        stat(m4, average_rate, "Average fee rate (sat/vB)")

        gap()

        chart_col, limits_col = st.columns([3, 2], gap="large")

        with chart_col:
            chart_title("Fee rate per transaction (sat/vB)")

            if mempool_df.empty:
                st.caption("Nothing to chart while the mempool is empty.")
            else:
                st.bar_chart(
                    mempool_df.sort_values(
                        "Fee rate (sat/vB)", ascending=False
                    )
                    .reset_index(drop=True)["Fee rate (sat/vB)"],
                    color=AMBER,
                    height=230,
                )

        with limits_col:
            panel(
                "Limits",
                [
                    ("Memory usage", f'{mempool_info.get("usage", 0):,} B'),
                    (
                        "Max mempool",
                        f'{mempool_info.get("maxmempool", 0) / 1e6:,.0f} MB',
                    ),
                    (
                        "Min relay fee",
                        f'{mempool_info.get("minrelaytxfee", 0) * 1e5:.1f} sat/vB',
                    ),
                    (
                        "Mempool min fee",
                        f'{mempool_info.get("mempoolminfee", 0) * 1e5:.1f} sat/vB',
                    ),
                ],
            )

        gap()
        st.markdown("**Unconfirmed transactions**")

        if mempool_df.empty:
            st.info(
                "The mempool is empty. Send a transaction, then check here "
                "before mining the next block."
            )
        else:
            st.caption(
                f"Showing up to 100 of {len(mempool_df)} transactions, "
                "highest fee rate first."
            )

            show_table(
                mempool_df.sort_values(
                    "Fee rate (sat/vB)", ascending=False
                ).head(100)
            )


# ==================================================
# BLOCKS
# ==================================================

with blocks_tab:
    gap()
    section("Blocks", "Recent blocks and a block inspector.")

    if blocks_df.empty:
        st.info("No block data available yet.")
    else:
        available = len(blocks_df)

        if available > 5:
            window = st.slider(
                "Blocks to show",
                min_value=5,
                max_value=available,
                value=min(20, available),
            )
        else:
            window = available

        view = blocks_df.tail(window)

        interval_mean = view["Interval (s)"].dropna().mean()

        b1, b2, b3 = st.columns(3)
        stat(b1, f'{view["Txs"].mean():.1f}', "Average transactions per block")
        stat(b2, fmt_bytes(view["Size (B)"].mean()), "Average block size")
        stat(
            b3,
            f"{interval_mean:.0f}s" if pd.notna(interval_mean) else "—",
            "Average time between blocks",
        )

        gap()

        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title("Transactions per block")
            st.bar_chart(view.set_index("Height")["Txs"], color=AMBER, height=220)

        with c2:
            chart_title("Block size (bytes)")
            st.line_chart(
                view.set_index("Height")["Size (B)"], color=AMBER, height=220
            )

        gap()
        st.markdown("**Latest blocks**")

        show_table(
            view.sort_values("Height", ascending=False)[
                ["Height", "Time", "Txs", "Size (B)", "Weight", "Hash"]
            ]
        )

    gap()
    st.markdown("**Inspect a block**")

    tip_height = blockchain["blocks"]
    default_height = min(st.session_state.get("inspect_height", tip_height), tip_height)

    with st.form("block_form"):
        height_input = st.number_input(
            "Block height",
            min_value=0,
            max_value=tip_height,
            value=default_height,
            step=1,
        )

        block_submitted = st.form_submit_button("Inspect block")

    if block_submitted:
        st.session_state["inspect_height"] = int(height_input)

    inspect_height = min(st.session_state.get("inspect_height", tip_height), tip_height)

    try:
        block = get_block_by_height(inspect_height, 2)

        panel(
            f"Block {block['height']:,}",
            [
                ("Time", fmt_time(block["time"])),
                ("Transactions", block["nTx"]),
                ("Size", f'{block["size"]:,} B'),
                ("Weight", f'{block["weight"]:,} WU'),
                ("Difficulty", f'{block["difficulty"]:.8f}'),
                ("Nonce", block["nonce"]),
                ("Confirmations", block["confirmations"]),
            ],
        )

        gap()
        st.markdown("**Hash**")
        st.code(block["hash"], language=None)

        if block.get("previousblockhash"):
            st.markdown("**Previous block**")
            st.code(block["previousblockhash"], language=None)

        block_txs = [
            {
                "Transaction ID": tx["txid"],
                "Type": "Coinbase"
                if tx.get("vin") and "coinbase" in tx["vin"][0]
                else "Transfer",
                "Inputs": len(tx.get("vin", [])),
                "Outputs": len(tx.get("vout", [])),
                "Total out (BTC)": sum(
                    float(out.get("value", 0)) for out in tx.get("vout", [])
                ),
                "vsize (vB)": tx.get("vsize"),
            }
            for tx in block.get("tx", [])
        ]

        st.markdown("**Transactions in this block**")
        show_table(block_txs)

        with st.expander("Raw JSON"):
            st.json(block)

    except Exception as error:
        st.error(f"Could not load block {inspect_height}: {error}")


# ==================================================
# WALLETS
# ==================================================

with wallets_tab:
    gap()
    section("Wallets", "Every loaded wallet, and the outputs of the selected one.")
    show_flash("wallets")

    if summary_rows:
        summary_df = pd.DataFrame(summary_rows)

        w1, w2, w3 = st.columns(3)
        stat(w1, len(summary_df), "Wallets loaded")
        stat(w2, f'{summary_df["Confirmed"].sum():,.2f}', "Confirmed BTC in total")
        stat(w3, f'{summary_df["Immature"].sum():,.2f}', "Immature BTC in total")

        gap()

        table_col, chart_col = st.columns([3, 2], gap="large")

        with table_col:
            show_table(summary_df)

        with chart_col:
            chart_title("Confirmed balance per wallet")
            st.bar_chart(
                summary_df.set_index("Wallet")["Confirmed"],
                color=AMBER,
                height=220,
            )

    gap()

    manage_left, manage_right = st.columns(2, gap="large")

    with manage_left:
        st.markdown("**Create a wallet**")

        with st.form("create_wallet_form"):
            new_wallet_name = st.text_input(
                "Wallet name",
                placeholder="bob",
            )

            create_submitted = st.form_submit_button(
                "Create wallet",
                type="primary",
            )

        if create_submitted:
            created = False

            try:
                create_wallet(new_wallet_name)
                created = True
            except Exception as error:
                st.error(f"Could not create the wallet: {error}")

            if created:
                set_flash(
                    "wallets",
                    "success",
                    f"Wallet {new_wallet_name.strip()} created and loaded.",
                )
                st.rerun()

    with manage_right:
        st.markdown("**Wallets on disk, not loaded**")

        on_disk = load("Wallet directory", list_wallet_dir, [])
        unloaded = [name for name in on_disk if name not in wallets]

        load_target = None

        if not unloaded:
            st.caption("Every wallet on disk is already loaded.")

        for name in unloaded:
            name_col, button_col = st.columns([3, 1])
            name_col.markdown(
                f'<div class="ledger"><div class="row"><span class="k">'
                f'{esc(name or "(default wallet)")}</span></div></div>',
                unsafe_allow_html=True,
            )

            if button_col.button("Load", key=f"load_wallet_{name}"):
                load_target = name

        if load_target is not None:
            loaded = False

            try:
                load_wallet(load_target)
                loaded = True
            except Exception as error:
                st.error(f"Could not load the wallet: {error}")

            if loaded:
                set_flash(
                    "wallets",
                    "success",
                    f'Wallet {load_target or "(default wallet)"} loaded.',
                )
                st.rerun()

    gap()
    st.markdown(f"**Unspent outputs · {wallet_label}**")

    if utxos:
        utxo_df = pd.DataFrame(
            [
                {
                    "Address": utxo.get("address", ""),
                    "Amount (BTC)": float(utxo["amount"]),
                    "Confirmations": utxo.get("confirmations", 0),
                    "Txid": utxo["txid"],
                    "Vout": utxo["vout"],
                }
                for utxo in utxos
            ]
        )

        u1, u2 = st.columns([3, 2], gap="large")

        with u1:
            show_table(utxo_df.sort_values("Amount (BTC)", ascending=False))

        with u2:
            chart_title("Output sizes (BTC)")
            st.bar_chart(
                utxo_df.sort_values("Amount (BTC)", ascending=False)
                .reset_index(drop=True)["Amount (BTC)"],
                color=AMBER,
                height=220,
            )
    else:
        st.info(
            "No spendable outputs. Mine blocks to this wallet, then wait for "
            "100 confirmations."
        )


# ==================================================
# TRANSACTION HISTORY
# ==================================================

with history_tab:
    gap()
    section("Transactions", f"Activity in {wallet_label}.")

    if history_df.empty:
        st.info("No transactions in this wallet yet.")
    else:
        filter_left, filter_right = st.columns([3, 1])

        with filter_left:
            categories = sorted(history_df["Category"].unique())
            chosen_categories = st.multiselect(
                "Categories",
                categories,
                default=categories,
            )

        with filter_right:
            show_count = st.selectbox(
                "Show last",
                [20, 50, 100, 500, 1000],
                index=0,
            )

        filtered = history_df[history_df["Category"].isin(chosen_categories)]
        filtered = filtered.tail(show_count)

        received = filtered.loc[
            filtered["Category"].isin(["receive", "generate"]), "Amount"
        ].sum()
        sent = -filtered.loc[filtered["Category"] == "send", "Amount"].sum()
        fees = -filtered["Fee"].sum()

        t1, t2, t3, t4 = st.columns(4)
        stat(t1, f"{received:,.4f}", "BTC received")
        stat(t2, f"{sent:,.4f}", "BTC sent")
        stat(t3, f"{fees:.8f}", "BTC paid in fees")
        stat(t4, len(filtered), "Transactions shown")

        gap()

        newest_first = filtered.iloc[::-1]
        show_table(newest_first)

        st.download_button(
            "Export CSV",
            newest_first.to_csv(index=False),
            file_name=f"transactions_{wallet or 'default'}.csv",
            mime="text/csv",
        )

    gap()

    recent_txids = (
        list(dict.fromkeys(reversed(history_df["Txid"].tolist())))[:50]
        if not history_df.empty
        else []
    )

    with st.expander("Inspect a transaction"):
        with st.form("lookup_form"):
            picked_txid = st.selectbox(
                "Pick a recent transaction",
                [""] + recent_txids,
                format_func=lambda txid: short(txid) if txid else "—",
            )

            typed_txid = st.text_input(
                "Or paste a transaction ID",
                key="lookup_txid",
            )

            lookup_submitted = st.form_submit_button("Inspect transaction")

        if lookup_submitted:
            lookup_txid = typed_txid.strip() or picked_txid

            if not lookup_txid:
                st.error("Pick a transaction or paste its ID.")

            else:
                try:
                    render_transaction(
                        get_transaction(wallet, lookup_txid, verbose=True)
                    )
                except Exception as error:
                    st.error(f"Transaction lookup failed: {error}")


# ==================================================
# NODE
# ==================================================

with node_tab:
    gap()
    section("Node", "Version, storage and network details from Bitcoin Core.")

    try:
        network_info = get_network_info()
        mining_info = get_mining_info()
        uptime_seconds = get_uptime()
        chain_tips = get_chain_tips()
        peers = get_peer_info()

    except Exception as error:
        st.error(f"Could not retrieve node information: {error}")

    else:
        node_left, node_right = st.columns(2, gap="large")

        with node_left:
            panel(
                "Bitcoin Core",
                [
                    ("Version", network_info.get("subversion", "—")),
                    ("Protocol", network_info.get("protocolversion", "—")),
                    ("Uptime", fmt_duration(uptime_seconds)),
                    (
                        "Connections",
                        f'{network_info.get("connections", 0)} '
                        f'({network_info.get("connections_in", 0)} in / '
                        f'{network_info.get("connections_out", 0)} out)',
                    ),
                    (
                        "Network active",
                        "yes" if network_info.get("networkactive") else "no",
                    ),
                ],
            )

        with node_right:
            panel(
                "Chain",
                [
                    ("Size on disk", fmt_bytes(blockchain.get("size_on_disk", 0))),
                    (
                        "Verification",
                        f'{blockchain.get("verificationprogress", 0) * 100:.2f}%',
                    ),
                    ("Median time", fmt_time(blockchain.get("mediantime", 0))),
                    ("Pooled transactions", mining_info.get("pooledtx", 0)),
                    (
                        "Network hash rate",
                        f'{mining_info.get("networkhashps", 0):,.0f} H/s',
                    ),
                ],
            )

        gap()
        st.markdown("**Chain tips**")
        show_table(
            [
                {
                    "Height": tip.get("height"),
                    "Status": tip.get("status"),
                    "Branch length": tip.get("branchlen"),
                    "Hash": tip.get("hash"),
                }
                for tip in chain_tips
            ]
        )

        gap()
        st.markdown("**Peers**")

        if peers:
            show_table(
                [
                    {
                        "Address": peer.get("addr"),
                        "Direction": "inbound"
                        if peer.get("inbound")
                        else "outbound",
                        "Version": peer.get("subver"),
                        "Ping (s)": peer.get("pingtime"),
                    }
                    for peer in peers
                ]
            )
        else:
            st.caption(
                "No peers connected. That is normal for a single regtest node."
            )


# ==================================================
# AUTO-REFRESH
# ==================================================

if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()