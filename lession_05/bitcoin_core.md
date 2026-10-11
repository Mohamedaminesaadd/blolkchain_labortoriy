The mempool (memory pool) is the place where a Bitcoin node keeps valid transactions it has received but that have not yet been confirmed in a block.

Think of it as a waiting room for transactions.

## 1. How the mempool works

1\. Sara creates a transaction

Sara sends 1 BTC to Omar and signs the transaction.

2\. Nodes validate and relay it

Nodes check the transaction and share it with their peers.

3\. The transaction waits in the mempool

It is unconfirmed. A miner may select it for a block.

4\. A miner includes it in a block

Once the block is accepted, the transaction has one confirmation.

## 2. Your Bitcoin lab example

Before you mined Block 103, your mempool contained these three transactions:

| Transaction   | Payment               | Fee            |
| ------------- | --------------------- | -------------- |
| `5a8d2080...` | Amine → Omar: 3 BTC   | 0.00000141 BTC |
| `befeb1c9...` | Amine → Master: 2 BTC | 0.00000141 BTC |
| `e2f00767...` | Sara → Omar: 1 BTC    | 0.00000141 BTC |

You checked with:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getrawmempool
```

All four of your nodes reported those transaction IDs. Then Amine mined Block 103, which contained the three transactions plus the coinbase transaction.

Before mining: 3 transactions were waiting in the mempool.

After mining: those transactions were confirmed in Block 103 and should no longer be in the mempool, assuming the nodes have synchronized and there are no other changes.

## 3. Check your mempool now

On Amine, run:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getrawmempool
```

To count the transactions:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getmempoolinfo
```

Look at the `size` field. It tells you how many transactions are currently in that node's mempool.

## 4. Important concepts

- Mempool is not the blockchain. It stores unconfirmed transactions locally.
- Each node has its own mempool. Nodes usually share many transactions, but their mempools can differ.
- A transaction in the mempool is not guaranteed to be mined. It could remain unconfirmed or be removed.
- Mining confirms transactions. A miner selects transactions, builds a candidate block, and tries to produce a valid block.
- The mempool is not a permanent ledger. The blockchain records confirmed blocks, while the mempool is temporary transaction storage.

One final detail: the mempool is not a single global waiting room shared by every Bitcoin node. It is a separate pool maintained by each node.



Bitcoin Core RPC Fundamentals means learning how to control, inspect, and interact with a Bitcoin node programmatically using the Remote Procedure Call (RPC) interface.

In your lab, you use `bitcoin-cli` to send commands to `bitcoind`. This is exactly what Bitcoin Core RPC is.

## 1. Understand the architecture

You — Terminal

Run bitcoin-cli commands

RPC interface

Request and response, typically JSON over HTTP

Your regtest RPC port: `18443`

Bitcoin Core — bitcoind

Blockchain, mempool, wallets, validation and P2P networking

There are two important programs:

- `bitcoind`: runs the Bitcoin node.
- `bitcoin-cli`: sends RPC requests to that node and displays the responses.

For example:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
```

Here, `bitcoin-cli` sends the `getblockchaininfo` RPC request to your node. The node returns information about its blockchain.

## 2. The five main categories of RPC commands

1\. Blockchain RPCs

Inspect blocks, chain height, and confirmations.

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockcount
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockhash 103
```

Example: find the hash of Block 103.

2\. Wallet RPCs

Create addresses, check balances, and send BTC.

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf -rpcwallet=miner getbalance
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf -rpcwallet=miner getnewaddress
```

Example: inspect Amine's miner wallet.

3\. Network RPCs

Inspect peers and transaction propagation.

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getpeerinfo
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getconnectioncount
```

Example: check whether Master is connected to other nodes.

4\. Mempool and transaction RPCs

Inspect unconfirmed transactions and transaction details.

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getrawmempool
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getmempoolinfo
```

Example: see which transactions are waiting for a block.

5\. Mining RPCs

In regtest, generate blocks and inspect their contents.

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf -rpcwallet=miner getnewaddress
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf -rpcwallet=miner generatetoaddress 1 ADDRESS
```

Replace `ADDRESS` with a valid address you control.

## 3. Understand the RPC command structure

Most of your commands follow this pattern:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf [OPTIONS] COMMAND [ARGUMENTS]
```

| Part                 | Meaning                                   |
| -------------------- | ----------------------------------------- |
| `bitcoin-cli`        | RPC client                                |
| `-conf=...`          | Use your custom configuration             |
| `-rpcwallet=miner`   | Select the `miner` wallet for wallet RPCs |
| `getbalance`         | RPC method                                |
| Additional arguments | Parameters for that method                |

For example:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockhash 103
```

The number `103` is the argument passed to the RPC method.

## 4. RPC versus P2P: a crucial distinction

These are two different communication systems.

| RPC                                           | P2P                                                   |
| --------------------------------------------- | ----------------------------------------------------- |
| You use it to control or query your own node. | Nodes use it to communicate with other nodes.         |
| Usually local in your current setup.          | Uses Bitcoin's P2P port, `18444` in your regtest lab. |
| Example: `getblockchaininfo`                  | Example: sharing transactions and blocks              |

When Sara sends 1 BTC to Omar, her wallet uses RPC to ask her local node to create and broadcast the transaction. The node then uses P2P to relay it to connected peers.

Your RPC command does not directly send the transaction to every node.

## 5. Why RPC failed on Master earlier

You encountered:

```
Could not connect to the server 127.0.0.1:18443
```

That is an RPC connection error, not necessarily a P2P networking error. It usually means `bitcoind` is stopped, still starting, or not listening on the expected RPC port.

On Master, you can check:

```
pgrep -a bitcoind
```

If it is not running, start it:

```
bitcoind -conf=/opt/bitcoin/bitcoin.conf
```

Then test:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
```

Do not delete the regtest data directory when troubleshooting this issue.

## 6. Your first RPC fundamentals exercise


Your goal: understand the RPC client, the RPC method, its arguments, and the returned JSON. Once you master these fundamentals, you can automate your Bitcoin lab with Python using Bitcoin Core's JSON-RPC interface.


### let's take example of mempoll
## 1. Inspecting the Memory Pool

To inspect the current state of the Bitcoin memory pool, execute the following command:

```bash
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getmempoolinfo
```

**Output:**

```json
{
  "loaded": true,
  "size": 0,
  "bytes": 0,
  "usage": 0,
  "total_fee": 0.00000000,
  "maxmempool": 300000000,
  "mempoolminfee": 0.00000100,
  "minrelaytxfee": 0.00000100,
  "incrementalrelayfee": 0.00000100,
  "unbroadcastcount": 0,
  "fullrbf": true,
  "permitbaremultisig": true,
  "maxdatacarriersize": 100000,
  "limitclustercount": 64,
  "limitclustersize": 101000,
  "optimal": true
}
```

### Interpretation

- **`loaded: true`** — The memory pool is loaded and ready.
- **`size: 0`** — There are currently no transactions in the memory pool.
- **`bytes: 0`** — The memory pool contains zero transaction-data bytes.
- **`usage: 0`** — The memory pool currently uses zero bytes of allocated memory.
- **`total_fee: 0.00000000`** — The total fees of transactions currently in the pool are zero BTC.
- **`maxmempool: 300000000`** — The configured maximum memory-pool memory limit is 300,000,000 bytes.
- **`mempoolminfee: 0.00000100`** — The current minimum memory-pool fee rate is 0.00000100 BTC per virtual byte.
- **`minrelaytxfee: 0.00000100`** — The minimum transaction relay fee rate is 0.00000100 BTC per virtual byte.
- **`fullrbf: true`** — Full Replace-by-Fee (RBF) is enabled, allowing eligible replacements without requiring the original transaction to signal RBF explicitly.
- **`optimal: true`** — Bitcoin Core reports that the memory pool is in its optimal state.

**Conclusion:** At the moment this command was executed, the memory pool was empty. This is normal if no transactions were waiting to be confirmed.

mohamed-amine@msi-Katana-GF76-11UC:~$ 
explain

The output of the `getmempoolinfo` command provides detailed information about the current state of the mempool in your Bitcoin node. Here's a breakdown of each field:


Your output shows that Amine's Bitcoin node has an empty mempool. This is expected if the transactions were included in Block 103 and no new unconfirmed transactions have arrived.

Let's understand every field.

## 1. Your mempool status

## Amine's mempool

Empty

Pending transactions

# 0

`size`

Mempool memory usage

# 0 B

`usage`

Total pending fees

# 0 BTC

`total_fee`

Maximum configured size

# 300 MB

`maxmempool`

## 2. Explanation of each field

| Field                 | Your value           | Meaning                                                                                 |
| --------------------- | -------------------- | --------------------------------------------------------------------------------------- |
| `loaded`              | `true`               | The mempool is loaded and ready.                                                        |
| `size`                | `0`                  | No transactions are currently waiting in this node's mempool.                           |
| `bytes`               | `0`                  | The total serialized transaction size is zero bytes.                                    |
| `usage`               | `0`                  | No memory is currently used for mempool entries.                                        |
| `total_fee`           | `0.00000000` BTC     | No fees are attached to transactions currently in the mempool.                          |
| `maxmempool`          | `300000000`          | Configured limit of 300,000,000 bytes, approximately 300 MB.                            |
| `mempoolminfee`       | `0.00000100` BTC/kvB | Current minimum mempool fee rate, expressed in BTC per 1,000 virtual bytes.             |
| `minrelaytxfee`       | `0.00000100` BTC/kvB | Minimum configured relay fee rate for ordinary transactions.                            |
| `incrementalrelayfee` | `0.00000100` BTC/kvB | Fee-rate increment used for certain replacement and mempool eviction policies.          |
| `unbroadcastcount`    | `0`                  | No transactions are currently tracked as awaiting successful broadcast.                 |
| `fullrbf`             | `true`               | Full Replace-By-Fee policy is enabled for eligible replacement transactions.            |
| `permitbaremultisig`  | `true`               | The node permits bare multisig outputs under its relevant policy settings.              |
| `maxdatacarriersize`  | `100000`             | Maximum configured data-carrier size in bytes for relevant outputs such as `OP_RETURN`. |
| `limitclustercount`   | `64`                 | Configured cluster-count limit used by current mempool policy.                          |
| `limitclustersize`    | `101000`             | Configured cluster-size limit, in virtual bytes, used by current mempool policy.        |
| `optimal`             | `true`               | The mempool is considered to be in its optimal state under the node's current policy.   |

## 3. Why is the mempool empty?

Remember your lab:

Before Block 103

3 pending transactions in the mempool

Amine → Omar: 3 BTC

Amine → Master: 2 BTC

Sara → Omar: 1 BTC

Amine mines Block 103

The miner includes all 3 transactions plus the coinbase transaction.

After Block 103

The three transactions are confirmed and removed from the mempool.

# Mempool size = 0

Your output is consistent with that sequence.

One distinction: an empty mempool does not mean that the blockchain is empty. It means this node currently has no unconfirmed transactions in its mempool.

## 4. Try this next: verify Block 103

Run on Amine:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockcount
```

Then:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockhash 103
```

Finally, inspect the block:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblock \
2c10e73d2eeb5b8856c31ca27a5def38b52616c899fad26812a8bd04974cba9d 1
```

You should see four transaction IDs, including the coinbase transaction. That lets you compare the confirmed transactions in Block 103 with the zero unconfirmed transactions in the mempool.


-----------------------------------------------------------------
### remote procedure call (RPC) fundamentals
# Bitcoin Core RPC — from fundamentals to advanced labs

Since you've already built your Bitcoin regtest network with Amine, Master, Omar, and Sara, the best next step is to learn RPC as a tool for operating, debugging, and automating a Bitcoin node.

RPC stands for Remote Procedure Call. It lets you ask Bitcoin Core to perform an operation or return information, without manually inspecting the blockchain database.

## 1. Understand the RPC architecture

Your application

Terminal, Python script, monitoring tool

Bitcoin JSON-RPC API

Request → method + parameters → JSON response

Your regtest RPC port: `18443`

Bitcoin Core (`bitcoind`)

Wallets · Blockchain · Mempool · P2P network · Mining

For example:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
```

- `bitcoin-cli` is the RPC client.
- `getblockchaininfo` is the RPC method.
- The node executes the request and returns JSON.
- Your command communicates with your local node; it does not query a global Bitcoin server.

RPC and P2P are different: RPC controls or queries your node; P2P connects your node to other Bitcoin nodes.

## 2. The RPC methods worth learning first

Run these on your Amine host, assuming Bitcoin Core is running.

A. Blockchain inspection

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockcount
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getchaintips
```

Learn the current height, chain state, and known chain tips.

B. Blocks and transactions

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockhash 103
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblock <HASH> 2
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getrawtransaction <TXID> true
```

Replace `<HASH>` and `<TXID>` with real values. Learn block headers, Merkle roots, transaction inputs, outputs, and fees. `getrawtransaction` generally requires the transaction to be in the mempool or `txindex`/block context to be available.

C. Wallets and UTXOs

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf -rpcwallet=miner getbalance
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf -rpcwallet=miner listunspent
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf -rpcwallet=miner getbalances
```

Understand the difference between a wallet's balance and the individual UTXOs it controls.

D. P2P network

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getpeerinfo
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getconnectioncount
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getnetworkinfo
```

Investigate peer connections, network services, and why transactions may not propagate.

E. Mempool and fees

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getmempoolinfo
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getrawmempool
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getmempoolentry <TXID>
```

See which transactions are pending and inspect a particular transaction's mempool entry. `getmempoolentry` only works while that transaction is in the mempool.

## 3. Learn how to discover RPC methods yourself

You don't need to memorize every command. Bitcoin Core provides help for its RPC API.

### List all available commands

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf help
```

### Understand one specific command

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf help sendtoaddress
```

Or:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf help getblock
```

The help output explains the parameters, their types, and the returned values. Some methods require a wallet to be loaded; others operate at the node level.

### Understand RPC errors

| Error                       | Typical cause                                                                     |
| --------------------------- | --------------------------------------------------------------------------------- |
| Could not connect to server | `bitcoind` is stopped, starting, or not listening on the expected RPC port.       |
| Wallet not loaded           | The requested wallet needs to be loaded.                                          |
| Invalid parameter           | An argument has the wrong type or format.                                         |
| Method not found            | The method name is incorrect or unavailable.                                      |
| Insufficient funds          | The wallet has no suitable spendable UTXOs for the requested transaction and fee. |

RPC debugging is an important practical skill: learn to interpret the error instead of immediately changing your configuration.

## 4. Advanced concept: build a transaction using RPC

So far, you've used `sendtoaddress`, which hides much of the transaction-building process.

A more advanced lab is to create and inspect a raw transaction yourself.

1\. Find an available UTXO

Use `listunspent` to identify the previous transaction ID, output index, and amount.

2\. Construct a raw transaction

Use `createrawtransaction` to specify the inputs and outputs.

3\. Fund and sign it

Use `fundrawtransaction` to handle fees and change, then `signrawtransactionwithwallet`.

4\. Inspect and broadcast

Use `decoderawtransaction` to inspect it and `sendrawtransaction` to broadcast the signed transaction.

This lab teaches you how Bitcoin transactions are constructed, signed, and broadcast. Use your regtest network so mistakes don't put real funds at risk.

## 5. Use RPC from Python

RPC is not limited to the terminal. You can use it to build monitoring tools, dashboards, or automated lab exercises.

Bitcoin Core exposes a JSON-RPC interface. Python can send HTTP requests to that interface using an HTTP client such as `requests`.

For example, this script reads the block height:

```
import requestsfrom requests.auth import HTTPBasicAuthRPC_URL = "http://127.0.0.1:18443"# Load credentials from your protected Bitcoin Core configuration.# Do not hardcode real credentials in source code.RPC_USER = "your_rpc_user"RPC_PASSWORD = "your_rpc_password"payload = {    "jsonrpc": "2.0",    "id": "lab-1",    "method": "getblockcount",    "params": [],}response = requests.post(    RPC_URL,    json=payload,    auth=HTTPBasicAuth(RPC_USER, RPC_PASSWORD),    timeout=10,)response.raise_for_status()result = response.json()if result.get("error"):    raise RuntimeError(result["error"])print("Current block height:", result["result"])
```

Important: this example requires matching RPC credentials and an RPC server configured to accept the connection. It is not ready to run unchanged with your current configuration, which uses local RPC settings. Never expose your RPC port publicly or commit credentials to Git.

## 6. Your RPC learning roadmap

Level 1 — RPC fundamentals

Start here

Commands, arguments, JSON output, help, errors, and configuration.

Level 2 — Blockchain and UTXOs

Inspect blocks, transactions, Merkle roots, balances, and spendable outputs.

Level 3 — Mempool and P2P

Diagnose peer connections, transaction propagation, fee policies, and confirmations.

Level 4 — Raw transactions

Create, fund, sign, decode, and broadcast transactions.

Level 5 — Automation

Write Python scripts that monitor all four nodes and compare their block heights, mempools, and balances.

My recommendation: start with a practical RPC lab using your four nodes. First learn `help`, `getblockchaininfo`, `getblock`, `listunspent`, and `getpeerinfo`. Then move to raw transactions and Python automation. This builds directly on the network you have already created.