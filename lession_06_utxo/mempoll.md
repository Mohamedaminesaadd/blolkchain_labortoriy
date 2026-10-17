# Lab 37 — Inspect the Bitcoin Mempool

## 1. Objective

Understand how Bitcoin Core stores and manages unconfirmed transactions before they are included in a block.

The mempool (memory pool) is a node's local collection of transactions that it has accepted but that are not yet confirmed in the blockchain.

Important: each Bitcoin node has its own mempool. Two nodes can have different mempool contents even when they are connected through P2P.

## 2. Command 1 — `getrawmempool`

List the transaction IDs currently in your node's mempool.

```
bitcoin-cli -regtest getrawmempool
```

Example output:

```
[
  "5239755c2c4d4b9097ab3cfea8dd78da999cc6378410209be133250d6039bec1",
  "e04696e68037ec28ed164fde03fa0e973f0c0f89895999bc21d762ea1852861e"
]
```

Each string is a transaction ID (`txid`).

To display the number of unconfirmed transactions:

```
bitcoin-cli -regtest getrawmempool | jq 'length'
```

If the result is `0`, the node's mempool is empty.

## 3. Command 2 — `getmempoolinfo`

Display statistics about the local mempool.

```
bitcoin-cli -regtest getmempoolinfo
```

Important fields:

| Field           | Meaning                                           |
| --------------- | ------------------------------------------------- |
| `loaded`        | Whether the mempool has been loaded               |
| `size`          | Number of transactions in the mempool             |
| `bytes`         | Total serialized transaction size in bytes        |
| `usage`         | Approximate memory usage                          |
| `total_fee`     | Total fees of mempool transactions, in BTC        |
| `mempoolminfee` | Current minimum mempool fee rate, in BTC/kvB      |
| `minrelaytxfee` | Minimum relay fee rate, in BTC/kvB                |
| `maxmempool`    | Configured maximum mempool memory usage, in bytes |

For example, if `size` is `4`, your node has four unconfirmed transactions in its mempool.

Remember that `total_fee` is the sum of transaction fees, not the total value transferred.

## 4. Command 3 — `getmempoolentry`

Inspect one specific unconfirmed transaction.

First, obtain a transaction ID:

```
bitcoin-cli -regtest getrawmempool
```

Then substitute the actual TXID:

```
bitcoin-cli -regtest getmempoolentry "TXID"
```

For your earlier Sara transaction, you can try:

```
bitcoin-cli -regtest getmempoolentry 5239755c2c4d4b9097ab3cfea8dd78da999cc6378410209be133250d6039bec1
```

This succeeds only if that transaction is currently in the node's mempool.

Key fields include:

- `vsize`: transaction virtual size in vbytes.
- `weight`: transaction weight.
- `fees.base`: transaction's own fee in BTC.
- `time`: time the node accepted the transaction.
- `height`: blockchain height when it entered the mempool.
- `ancestorcount`: number of unconfirmed transactions in its ancestry, including itself.
- `descendantcount`: number of transactions in its descendant set, including itself.
- `depends`: unconfirmed transactions this transaction depends on.

## 5. Practical experiment

Run these commands on Amine, Sara, and Omar, one node at a time.

## Mempool inspection checklist

Select the node you are inspecting, then run the commands in its terminal.

Amine

Sara

Omar

```
bitcoin-cli -regtest getrawmempool
bitcoin-cli -regtest getmempoolinfo
```

Transaction ID to inspect

&#x20;Copy entry command

Selected node: amine. Run the copied command in that node's terminal.

### Questions to answer

1. How many transactions are in each node's mempool?
2. Does Sara's transaction appear in Amine's and Omar's mempools?
3. What is the transaction's fee in BTC and its virtual size?
4. If a transaction appears in Sara's mempool but not Omar's, what might explain the difference?

Expected lesson: a transaction being accepted into one node's mempool does not guarantee that every peer has received or accepted it. Mempool inspection lets you investigate propagation and transaction acceptance before mining.


inspect the transaction in Sara's mempool:
```bitcoin-cli -regtest getmempoolentry "48abdd005628299ae6788af124637833c3259accf3a74bb08a0b4adbae1d80a5"```
```

{
  "vsize": 141,
  "weight": 561,
  "time": 1792230072,
  "height": 120,
  "descendantcount": 1,
  "descendantsize": 141,
  "ancestorcount": 1,
  "ancestorsize": 141,
  "wtxid": "7f6b5f49eee7ad85530566d8e7f57a41a36320e43c3f974bbae279cc9c760ba0",
  "chunkweight": 561,
  "fees": {
    "base": 0.00000141,
    "modified": 0.00000141,
    "ancestor": 0.00000141,
    "descendant": 0.00000141,
    "chunk": 0.00000141
  },
  "depends": [
  ],
  "spentby": [
  ],
  "bip125-replaceable": true,
  "unbroadcast": false
}

```

--------------------------------------------------------------
In Bitcoin Core, the mempool is not a traditional database such as MySQL, PostgreSQL, or MongoDB. It is primarily an in-memory data structure managed by the Bitcoin Core node.

## 1. What data structure does it use?

Bitcoin Core's mempool is implemented in C++ using data structures such as hash maps and ordered indexes to manage transactions efficiently.

- Hash-based indexes: efficiently find transactions by their transaction ID (`txid`).
- Ordered indexes: organize transactions by properties such as fee rate, helping the node select transactions for block construction and manage its mempool.
- Dependency tracking: records relationships between unconfirmed transactions, such as a child transaction spending an output from a parent transaction.

The central implementation is called `CTxMemPool`.

## 2. How does it store transactions?

Incoming P2P transaction

Validation

Scripts, inputs, fees, conflicts and other rules

CTxMemPool — RAM

Accepted unconfirmed transactions and indexes

Block confirmation

The transaction is included in a block and removed from the mempool.

## 3. Is the mempool persistent?

Normally, the mempool is held in RAM, but Bitcoin Core can save a snapshot to disk in a file called `mempool.dat` when configured to persist the mempool. It can load that snapshot again when restarting.

This file is not the blockchain database and is not a replacement for the node's authoritative blockchain data.

You can inspect the relevant settings with:

```
bitcoin-cli -regtest getmempoolinfo
bitcoin-cli -regtest getmempoolentry "TXID"
```

## 4. Mempool vs blockchain storage

| Feature               | Mempool                                            | Blockchain storage                                |
| --------------------- | -------------------------------------------------- | ------------------------------------------------- |
| Main storage          | RAM                                                | Disk                                              |
| Contents              | Accepted unconfirmed transactions                  | Blocks and confirmed transaction history          |
| Shared between nodes? | No, each node has its own                          | Nodes independently store and validate chain data |
| Survives restart?     | Not guaranteed; may be reloaded from `mempool.dat` | Yes, stored on disk                               |
| Main purpose          | Manage pending transactions                        | Maintain the blockchain                           |

Key takeaway: Bitcoin Core's mempool is an in-memory transaction pool built with specialized C++ data structures, with optional disk persistence. It is not a standalone SQL or NoSQL database.

# Bitcoin Regtest Labs 38–40: Propagation, Synchronization, and Fees

These three labs build on your Bitcoin Core network with the Amine, Omar, and Sara nodes. You will observe how a transaction moves through the P2P network, why nodes can have different mempools, and how transaction fees influence which transactions miners select.

## Lab 38 — Transaction Propagation Between Nodes

### Objective

Create a transaction on Amine, then observe whether Omar and Sara receive and accept the same transaction.

Your target topology is:

Amine

Creates the transaction

Transaction: TXID

Omar

Receives and validates

Sara

Receives and validates

A key distinction: this diagram represents the propagation path you want to study. Bitcoin Core normally relays transactions to eligible peers; it does not automatically guarantee that every transaction travels through exactly this path. Your actual peer connections determine the possible routes.

### Step 1 — Check the P2P connections

Run this on each node:

```
bitcoin-cli -regtest getpeerinfo
```

Confirm that Amine is connected to Omar and Omar is connected to Sara. Use the peer addresses to identify the connections.

### Step 2 — Create a transaction on Amine

First, make sure Amine's wallet has spendable funds:

```
bitcoin-cli -regtest -rpcwallet=amine getbalance
```

Generate a fresh receiving address on Omar:

```
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

Copy the returned address. On Amine, send a small amount to that address:

```
bitcoin-cli -regtest -rpcwallet=amine sendtoaddress "OMAR_ADDRESS" 1
```

Save the returned transaction ID. That is your `TXID`.

If the wallet names or RPC wallet loading differ on your nodes, use the wallet name actually configured on each node.

### Step 3 — Inspect the transaction on all three nodes

On Amine, Omar, and Sara, run:

```
bitcoin-cli -regtest getrawmempool
```

Check whether your TXID appears. Then try:

```
bitcoin-cli -regtest getmempoolentry "TXID"
```

The second command succeeds only if that transaction is in the node's mempool.

Record the results before mining a block.

| Node  | TXID in mempool? |
| ----- | ---------------- |
| Amine | Expected: yes    |
| Omar  | Observe          |
| Sara  | Observe          |

If Omar receives the transaction but Sara does not, investigate Omar's peer connections, relay behavior, and Sara's transaction acceptance. A missing TXID does not by itself tell you which cause is responsible.

### Step 4 — Inspect the transaction itself

```
bitcoin-cli -regtest getrawtransaction "TXID" true
```

This returns decoded transaction details if the node has the transaction available through its mempool or accessible transaction data. Otherwise, the command may return an error.

Look at:

- `txid`: transaction identifier.
- `vin`: the previous outputs being spent.
- `vout`: the newly created outputs.
- `vout[].value`: amounts sent to recipients or returned as change.

Expected result: when all three nodes accept the transaction, they report the same TXID and transaction contents, even though the transaction is still unconfirmed.

## Lab 39 — Mempool Synchronization

### Objective

Understand why Amine, Omar, and Sara can be connected to the same P2P network but have different mempool contents.

Think of each node as maintaining its own local pending-transaction list:

### Amine

TX-A

TX-B

TX-C

### Omar

TX-A

TX-C

### Sara

TX-A

TX-D

Illustrative example: TX-B, TX-C, and TX-D are not present in every node's mempool.

### Step 1 — Compare the mempools

Run on each node:

```
bitcoin-cli -regtest getrawmempool
bitcoin-cli -regtest getmempoolinfo
```

Record the number of transactions and their TXIDs.

### Step 2 — Explain the differences

Mempools are not necessarily identical for several reasons:

1. Propagation delay: a transaction may reach one node before another.
2. Different peer connections: nodes may not receive transactions through the same routes.
3. Different acceptance rules or configuration: fee policies and other local settings can cause a node to reject a transaction that another accepts.
4. Missing or invalid inputs: a transaction may reference outputs that the node does not recognize as available.
5. Conflicts: a node may already have a transaction spending the same output.
6. Eviction and resource limits: nodes can remove transactions when mempool limits are reached.
7. Confirmation: once a transaction is mined, it is removed from the mempool as part of block processing.

### Step 3 — Compare blockchain state too

On all three nodes:

```
bitcoin-cli -regtest getblockchaininfo
```

Compare `blocks` and `bestblockhash`.

If the nodes have different chain histories, a transaction valid on one node may be invalid on another. Before diagnosing propagation, make sure the nodes are following the same regtest chain.

Expected lesson: P2P connectivity does not mean identical mempools. Each node independently receives, validates, and manages transactions.

## Lab 40 — Fee and Mempool Experiments

### Objective

Create transactions with different fee rates and observe how fee policies and miner selection affect confirmation.

The important distinction is that a transaction's fee is not the same as its fee rate.

\\[ \text{Fee} = \text{input value} - \text{output value} \\]

\\[ \text{Fee rate} = \frac{\text{fee in satoshis}}{\text{virtual size in vbytes}} \\]

For example, a 300-satoshi fee on a 150-vbyte transaction gives a fee rate of \\(2\\) sat/vB.

### Step 1 — Inspect current fee policy

```
bitcoin-cli -regtest getmempoolinfo
bitcoin-cli -regtest getnetworkinfo
```

Look for `mempoolminfee`, `minrelaytxfee`, and the node's fee configuration. Fee values in these RPC results are generally expressed in BTC/kvB, so convert units carefully before comparing them with sat/vB.

### Step 2 — Create transactions at different fee rates

On Amine, inspect the available fee-estimation options:

```
bitcoin-cli -regtest help sendtoaddress
bitcoin-cli -regtest help settxfee
```

For this experiment, you can use `settxfee` to set a wallet fee rate in BTC/kvB, then create a transaction:

```
bitcoin-cli -regtest -rpcwallet=amine settxfee 0.00002000
```

```
bitcoin-cli -regtest -rpcwallet=amine sendtoaddress "RECIPIENT_ADDRESS" 1
```

The example fee rate is 2,000 sat/vB? No — it is 2 sat/vB: \\(0.00002000\\) BTC/kvB equals 2,000 sat/kvB, or 2 sat/vB.

Repeat with a different fee setting and a fresh transaction. Record each TXID, its actual fee, and its virtual size using:

```
bitcoin-cli -regtest getmempoolentry "TXID"
```

Note that `settxfee` is a wallet fee setting, not a command to override every node's relay policy. Actual fee selection and acceptance also depend on wallet behavior, transaction size, and node configuration.

### Step 3 — Observe miner selection

In regtest, you can explicitly mine a block to a fresh address:

```
MINER_ADDRESS=$(bitcoin-cli -regtest -rpcwallet=amine getnewaddress)
bitcoin-cli -regtest generatetoaddress 1 "$MINER_ADDRESS"
```

Then inspect the mined block:

```
bitcoin-cli -regtest getblockchaininfo
bitcoin-cli -regtest getrawmempool
```

To identify which transactions were included, obtain the new block hash and decode the block:

```
BLOCK_HASH=$(bitcoin-cli -regtest getblockhash "$(bitcoin-cli -regtest getblockchaininfo | jq -r '.blocks')")
bitcoin-cli -regtest getblock "$BLOCK_HASH" 2
```

Important: regtest mining is controlled by your command, and a block can include transactions according to the node's block-template selection. It is not a realistic simulation of competitive mainnet mining. Higher fee rates often make transactions more attractive to miners because block space is limited, but a higher fee does not guarantee earlier confirmation.

### Step 4 — Record your experiment

| TXID | Fee (sats) | Virtual size (vB) | Fee rate (sat/vB) | Confirmed? |
| ---- | ---------- | ----------------- | ----------------- | ---------- |
| TX-A |            |                   |                   |            |
| TX-B |            |                   |                   |            |
| TX-C |            |                   |                   |            |

Calculate each fee rate by dividing the fee in satoshis by the virtual size in vbytes.

## Final understanding

- Lab 38: How transactions propagate between P2P nodes.
- Lab 39: Why each node can have a different mempool.
- Lab 40: How transaction fees, fee policies, and block construction affect confirmation.

For your lab report, save the RPC outputs from each node and compare the results before and after mining. That gives you concrete evidence of propagation, mempool differences, and confirmation behavior.

---------------------------------------------------------------
Yes! On the Bitcoin mainnet, a transaction can propagate through a large network of nodes worldwide using the Bitcoin P2P protocol. But it does not get sent directly to every node simultaneously.

## How a transaction propagates on mainnet

Imagine Alice sends 0.1 BTC to Bob.

Alice's wallet

Creates and broadcasts the transaction

Node A

Validates and accepts it into its mempool

Node B

Receives and validates

Node C

Receives and validates

Node D

Relays to more peers

Node E

Relays to more peers

Propagation continues across eligible peer connections throughout the network.

## The propagation cycle

1. Creation: Alice's wallet constructs and signs the transaction.
2. Broadcast: The wallet sends it to one or more Bitcoin nodes.
3. Validation: Each receiving node checks the transaction, including its inputs, signatures, and local acceptance policies.
4. Relay: If accepted, the node announces the transaction to eligible peers, which may request the transaction data.
5. Propagation: Other nodes repeat the process, allowing the transaction to spread through the network.
6. Mining: A miner may select the transaction for a block.
7. Confirmation: Once the block is accepted into the active chain, the transaction is confirmed.

## Does every node receive the transaction?

No, not necessarily. Propagation is best-effort, not a guarantee of universal delivery.

- Some nodes may be offline or not connected through a path that delivers the transaction.
- Nodes may reject transactions because of invalid inputs, conflicts, or local mempool and fee policies.
- Some nodes do not relay transactions, and propagation can be delayed.
- Wallets may submit transactions through specialized services rather than broadcasting directly to the public P2P network.

Also, nodes do not necessarily forward every transaction to every peer. Bitcoin uses announcements and transaction-request mechanisms to manage network traffic and avoid unnecessary duplicate transfers.

## What happens when the transaction is mined?

A miner includes the transaction in a candidate block and broadcasts the block. Nodes validate the block and update their chain state. The transaction is then removed from their mempools as appropriate.

A transaction can be propagated and still have zero confirmations. Propagation means nodes have received it; confirmation means it has been included in an accepted block.

The mainnet also has no single global mempool. Every node maintains its own local mempool, so two nodes can temporarily—or sometimes persistently—have different unconfirmed transactions.