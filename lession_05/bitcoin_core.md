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
mohamed-amine@msi-Katana-GF76-11UC:~$ bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getmempoolinfo
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