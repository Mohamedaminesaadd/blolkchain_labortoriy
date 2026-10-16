# Bitcoin Transaction — Inputs, Outputs, and UTXOs

A Bitcoin transaction is a message that tells the Bitcoin network how existing bitcoins should be spent and where the resulting bitcoins should go.

A normal Bitcoin transaction has inputs (`vin`) and outputs (`vout`).

- Input: references an existing UTXO that the transaction wants to spend.
- Output: creates a new amount of bitcoin locked by spending conditions.
- UTXO: an output that has not yet been spent.

## 1. How a Bitcoin transaction works

Imagine Omar has a UTXO worth 3 BTC and wants to send Sara 1 BTC.

Omar's existing UTXO

# 3 BTC

Created by an earlier transaction

New transaction

Spends the 3 BTC input

Output 0

## 1 BTC

Sara's receiving output

Output 1

## 1.9999 BTC

Omar's change output

Transaction fee: 0.0001 BTC

The arithmetic is:

```
Total inputs  = 3.0000 BTC
Total outputs = 2.9999 BTC
Fee           = 0.0001 BTC
```

Bitcoin does not modify the original 3 BTC UTXO into 2 BTC. It consumes the old output and creates two new outputs.

## 2. What does an input look like?

In Bitcoin Core's decoded transaction, inputs appear in the `vin` array.

Example:

```
{
  "vin": [
    {
      "txid": "previous_transaction_id",
      "vout": 0,
      "scriptSig": {},
      "txinwitness": ["..."]
    }
  ]
}
```

The values are illustrative.

- `txid`: identifies the previous transaction.
- `vout`: identifies which output of that transaction is being spent.
- `scriptSig` and/or `txinwitness`: provide the data needed to satisfy the previous output's spending conditions, depending on the output type.

For example, `txid` plus `vout: 0` identifies the first output of the previous transaction.

An input normally does not directly say "spend 1 BTC." Instead, it references a previous output whose value is recorded in the blockchain.

## 3. What does an output look like?

Outputs appear in the `vout` array.

```
{
  "vout": [
    {
      "value": 1.00000000,
      "n": 0,
      "scriptPubKey": {
        "address": "SARA_ADDRESS",
        "type": "witness_v0_keyhash"
      }
    },
    {
      "value": 1.99990000,
      "n": 1,
      "scriptPubKey": {
        "address": "OMAR_CHANGE_ADDRESS",
        "type": "witness_v0_keyhash"
      }
    }
  ]
}
```

The addresses and amounts here are examples.

- `value`: amount in BTC.
- `n`: output index, also known as `vout` when this output is referenced by a later transaction.
- `scriptPubKey`: the locking script that defines how the output can be spent.

An output is not necessarily assigned to a named person. It is locked by conditions, often associated with a Bitcoin address.

## 4. What happens to the UTXOs?

Before the transaction

Old UTXO

Outpoint: previous_txid:0

### 3 BTC

After the transaction is confirmed

Old UTXO

Spent; no longer in the UTXO set

New output 0

Sara can spend it under its locking conditions

### 1 BTC

New output 1

Omar can spend the change under its locking conditions

### 1.9999 BTC

The old transaction remains in the blockchain history, but its 3 BTC output is no longer an unspent output.

## 5. How to inspect a real transaction in your lab

First, list Omar's wallet transactions:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions "*" 10
```

Copy a transaction ID (`txid`), then decode it:

```
bitcoin-cli -regtest getrawtransaction "TXID" true
```

If the transaction is not available through this RPC, you may need to retrieve it through the wallet or inspect the block containing it.

Look for:

```
vin  = inputs: previous outputs being spent
vout = outputs: new outputs being created
```

For the exact output value and spending conditions, inspect a `vout` entry. For the previous output being consumed, use its input's `txid` and `vout` to inspect that outpoint.

## 6. Remember the difference

| Concept         | Meaning                                            |
| --------------- | -------------------------------------------------- |
| Transaction     | The complete spending operation                    |
| Input (`vin`)   | References an existing output to spend             |
| Output (`vout`) | Creates a new amount locked by spending conditions |
| UTXO            | An output that remains unspent                     |
| Fee             | Input value minus total output value               |

The key idea: inputs consume old UTXOs, outputs create new UTXOs, and the fee is the difference between the input and output totals.
---------------------------------------------------------------------------------------------
A UTXO lives in the UTXO set maintained by a Bitcoin full node, not inside a wallet or at a Bitcoin address.

## Where is it stored?

On your Ubuntu machine running Bitcoin Core in `regtest`, the default location is:

```
~/.bitcoin/regtest/chainstate/
```

This is Bitcoin Core's local database for the current UTXO state.

```
Bitcoin Core node (Omar)
        |
        +-- Blockchain data
        |      All historical blocks and transactions
        |
        +-- Chainstate database
        |      Current UTXO set
        |      (unspent outputs)
        |
        +-- Wallet "omar"
               Keys, addresses, transaction history,
               and UTXOs relevant to Omar
```

## How does a UTXO get there?

1. A transaction creates an output.
2. When the transaction is confirmed in the active blockchain, Bitcoin Core updates its UTXO set.
3. When another confirmed transaction spends that output, Bitcoin Core removes it from the UTXO set.

The original output remains recorded in blockchain history even after it is spent.

## Verify it in your lab

Check the node's UTXO set statistics:

```
bitcoin-cli -regtest gettxoutsetinfo
```

Check one particular output:

```
bitcoin-cli -regtest gettxout "TXID" 0
```

List outputs relevant to Omar's wallet:

```
bitcoin-cli -regtest -rpcwallet=omar listunspent
```

Remember: `chainstate` stores the node-wide UTXO set; Omar's wallet tracks only the outputs relevant to that wallet. The UTXO is a record in Bitcoin Core's database, not a separate file for each coin.

--------------------------------------------------------------
A UTXO lives in the UTXO set maintained by a Bitcoin full node, not inside a wallet or at a Bitcoin address.

## Where is it stored?

On your Ubuntu machine running Bitcoin Core in `regtest`, the default location is:

```
~/.bitcoin/regtest/chainstate/
```

This is Bitcoin Core's local database for the current UTXO state.

```
Bitcoin Core node (Omar)
        |
        +-- Blockchain data
        |      All historical blocks and transactions
        |
        +-- Chainstate database
        |      Current UTXO set
        |      (unspent outputs)
        |
        +-- Wallet "omar"
               Keys, addresses, transaction history,
               and UTXOs relevant to Omar
```

## How does a UTXO get there?

1. A transaction creates an output.
2. When the transaction is confirmed in the active blockchain, Bitcoin Core updates its UTXO set.
3. When another confirmed transaction spends that output, Bitcoin Core removes it from the UTXO set.

The original output remains recorded in blockchain history even after it is spent.

## Verify it in your lab

Check the node's UTXO set statistics:

```
bitcoin-cli -regtest gettxoutsetinfo
```

Check one particular output:

```
bitcoin-cli -regtest gettxout "TXID" 0
```

List outputs relevant to Omar's wallet:

```
bitcoin-cli -regtest -rpcwallet=omar listunspent
```

Remember: `chainstate` stores the node-wide UTXO set; Omar's wallet tracks only the outputs relevant to that wallet. The UTXO is a record in Bitcoin Core's database, not a separate file for each coin.

--------------------------------------------------------------
Yes. If your node runs Bitcoin Core as a fully validating node and has fully synchronized with the real Bitcoin mainnet, its UTXO set contains all currently unspent transaction outputs in the active mainnet blockchain, not just the outputs belonging to your wallet.

## 1. What does your node store?

Imagine your Bitcoin mainnet node:

```
Bitcoin Mainnet Node
        |
        +-- Blockchain database
        |      Historical blocks and transactions
        |
        +-- LevelDB: chainstate
        |      All current UTXOs in the active chain
        |      (not just your own bitcoins)
        |
        +-- Your wallet
               Your keys, addresses, and wallet-related transactions
```

For example, the node's UTXO set could conceptually contain:

```
UTXO A → 3 BTC → belongs to Wallet A
UTXO B → 0.5 BTC → belongs to Wallet B
UTXO C → 12 BTC → belongs to Wallet C
UTXO D → 0.01 BTC → ownership unknown to your wallet
...
Millions of other outputs
```

These are illustrative examples, not live network data.

Your node maintains the UTXO set needed to validate transactions, even when the outputs belong to strangers and your wallet has no knowledge of their private keys.

## 2. Does it contain every output ever created?

No. It contains the outputs that remain unspent in the active chain.

| Output state                                             | In the current UTXO set?                 |
| -------------------------------------------------------- | ---------------------------------------- |
| Created and never spent                                  | Yes                                      |
| Created and later spent                                  | No                                       |
| Created in a block that is no longer in the active chain | No                                       |
| Unconfirmed transaction output                           | Not in the confirmed chainstate UTXO set |

Historical outputs that have been spent remain recorded in the blockchain's transaction history. They are not part of the current UTXO set.

## 3. How can you inspect it?

On a fully synchronized mainnet node, you can run:

```
bitcoin-cli getblockchaininfo
```

Check that:

```
"chain": "main"
"initialblockdownload": false
```

Then inspect the UTXO set statistics:

```
bitcoin-cli gettxoutsetinfo
```

This returns information such as the number of unspent outputs (`txouts`) and their aggregate value (`total_amount`), depending on the output format.

To check a particular outpoint:

```
bitcoin-cli gettxout "TXID" 0
```

Replace the transaction ID and output index with real values.

## 4. Important distinction: full node versus pruned node

A pruned Bitcoin Core node can still fully validate the blockchain and maintain the current UTXO set, even though it deletes older block files to save disk space.

So:

- Full archival node: retains historical block data and maintains the current UTXO set.
- Pruned full node: maintains the current UTXO set but discards older block data according to its pruning configuration.
- Wallet: tracks only the outputs relevant to the wallet, not the entire network-wide UTXO set.

The key idea is that your node does not need to own bitcoins to maintain the UTXOs. It maintains this shared state to verify that transactions on the network spend valid, unspent outputs.
----------------------------------------------------------------
# What happens if two people try to spend the same UTXO at almost the same time?

This is called a double-spend attempt. Bitcoin's transaction validation and consensus rules prevent both conflicting transactions from being confirmed in the same valid chain history.

Imagine that Amine owns one UTXO worth 3 BTC. He creates two conflicting transactions:

- Transaction A: send 3 BTC to Sara.
- Transaction B: send 3 BTC to Omar.

Both transactions reference the same UTXO.

## 1. The conflict

Original UTXO

# 3 BTC

One outpoint: txid + vout

### Transaction A

Pay Sara

Conflicting spend

### Transaction B

Pay Omar

Conflicting spend

Both transactions attempt to consume the same original output.

## 2. What do Bitcoin nodes do?

### Step 1 — Transactions arrive

Suppose one node receives Transaction A first and another node receives Transaction B first.

Each node independently validates the transaction it receives, including checking signatures, spending conditions, and whether the input is available.

### Step 2 — Nodes may temporarily disagree

One node might accept Transaction A into its mempool and reject Transaction B as a conflict. Another node might accept Transaction B first.

This can happen because mempools are local and transaction propagation takes time.

Mempool acceptance is not confirmation. It does not guarantee that the transaction will be included in a block.

### Step 3 — A miner selects a transaction

A miner might include Transaction A in a candidate block.

If that block is valid and becomes part of the active chain, Transaction A spends the original UTXO. Transaction B can no longer spend that same output in the resulting chain history.

```
Original UTXO: 3 BTC
        |
        v
Transaction A included in a valid block
        |
        v
Original UTXO is spent
        |
        v
Transaction B conflicts with the confirmed spend
```

The miner could instead include Transaction B. The outcome depends on which transaction gets included in the accepted chain, not simply which was broadcast first or which pays a higher fee.

## 3. What if both transactions are mined?

It depends on the chain history.

- If both conflicting transactions appear in the same block, the block is invalid under Bitcoin's consensus rules because the second spend cannot consume an already-spent output.
- If they appear in different competing blocks, only a valid chain history can remain active. When the chain reorganizes, the transaction in the block that is no longer active may become unconfirmed again, or be rejected from the mempool if it conflicts with the winning chain.

So Bitcoin does not permit both conflicting spends to remain confirmed in the same valid chain history.

## 4. How does the UTXO set prevent double spending?

The node maintains the current UTXO set in its chainstate database.

When validating a transaction, it checks that each input references an available output. When a valid block is connected, the node updates the UTXO set by removing spent outputs and adding new outputs.

This makes the same outpoint unavailable for a second spend in that chain state.

## 5. Can you test this in your regtest lab?

Yes. Use a disposable test wallet and a funded UTXO on your regtest network. Construct two separately signed transactions that spend the same input but pay different destinations. Broadcast one, then try broadcasting the other.

Bitcoin Core will typically reject the conflicting transaction from the mempool, though the exact error depends on how the transactions were constructed and the node's current state.

Do not use real mainnet funds for this experiment.

## Questions to explore next

1. Why might two nodes accept different transactions into their mempools?
2. What is a blockchain reorganization, and how can it affect a transaction's confirmation?
3. How do transaction fees influence which conflicting transaction a miner chooses?
4. Why do merchants often wait for multiple confirmations before treating a Bitcoin payment as final?
-----------------------------------------------------------
# 1. Difference between a mempool transaction and a confirmed transaction

The main difference is whether the transaction has been included in a block that belongs to the active blockchain.

## A. Mempool transaction

A mempool (memory pool) is a node's collection of valid, unconfirmed transactions that the node is keeping for potential inclusion in a block.

Suppose Amine sends 2 BTC to Sara.

```
Amine creates transaction
          |
          v
Signs transaction
          |
          v
Bitcoin node validates it
          |
          v
Transaction enters mempool
          |
          v
Waiting for a miner
```

At this point:

- The transaction has not yet been confirmed in a block.
- Other nodes may have received it, but mempools can differ.
- The transaction can be delayed or dropped from a node's mempool.
- A conflicting transaction might replace it under applicable mempool policy.

A transaction in the mempool is not guaranteed to be confirmed.

## B. Confirmed transaction

A transaction becomes confirmed when it is included in a valid block that is accepted into the active blockchain.

```
Transaction in mempool
          |
          v
Miner selects transaction
          |
          v
Transaction included in block
          |
          v
Block accepted into active chain
          |
          v
Transaction has 1 confirmation
          |
          v
More blocks are added
          |
          v
2, 3, 4... confirmations
```

Each additional block built on top of the transaction's block increases its confirmation count.

| State           | Meaning                                                          |
| --------------- | ---------------------------------------------------------------- |
| 0 confirmations | Not included in the active chain; often unconfirmed in a mempool |
| 1 confirmation  | Included in a block in the active chain                          |
| 6 confirmations | Its block has five additional blocks built on top of it          |

A transaction can temporarily lose its confirmations if a blockchain reorganization removes its block from the active chain. Confirmations increase confidence, but they are not an absolute guarantee against every possible reorganization.

### How to inspect this in your lab

Show transactions in Omar's wallet:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions "*" 10
```

Check the mempool on the node:

```
bitcoin-cli -regtest getrawmempool
```

Inspect a transaction's confirmation count:

```
bitcoin-cli -regtest -rpcwallet=omar gettransaction "TXID"
```

Look for `confirmations`. A positive value indicates confirmation in the active chain; zero typically indicates an unconfirmed transaction.

# 2. How does a miner choose transactions for a block?

A miner generally tries to maximize the economic value of the transactions it includes while respecting Bitcoin's block and consensus rules.

## Step 1 — Transactions arrive at nodes

Users broadcast signed transactions to the Bitcoin network.

Nodes independently validate them and may accept them into their mempools.

```
User transactions
       |
       v
Bitcoin nodes
       |
       v
Node mempools
       |
       v
Miner builds candidate block
```

A miner normally selects from its own node's mempool, so two miners can have different candidate transactions.

## Step 2 — The miner evaluates transaction fees

Consider these example transactions:

| Transaction | Fee        | Virtual size | Fee rate   |
| ----------- | ---------- | ------------ | ---------- |
| A           | 1,000 sats | 200 vB       | 5 sats/vB  |
| B           | 6,000 sats | 300 vB       | 20 sats/vB |
| C           | 2,000 sats | 100 vB       | 20 sats/vB |

The fee rate is:

\\[ \text{Fee rate}=\frac{\text{Fee in satoshis}}{\text{Virtual size in vB}} \\]

For Transaction A:

\\[ \frac{1000}{200}=5\text{ sats/vB} \\]

Transaction C has the same fee rate as B, but it is smaller and pays a lower total fee. Both can be attractive, depending on the rest of the candidate block.

Miners often prioritize transactions with high fee rates because block space is limited.

## Step 3 — The miner checks dependencies

A transaction can depend on an unconfirmed transaction.

For example:

```
Transaction A:
  Creates an output worth 1 BTC

Transaction B:
  Spends that output
```

Transaction B cannot be confirmed in a block unless its parent transaction A is also available in the valid chain history or is included earlier in the same block.

Miners therefore consider transaction dependencies and may select a package of related transactions based on its combined fee rate.

## Step 4 — The miner builds a candidate block

The miner must respect constraints including:

- Valid transaction inputs and signatures.
- No double spending within the block.
- Block weight limits.
- Transaction dependencies.
- Consensus rules governing the block and its coinbase reward.

The miner constructs the block and performs the mining process. On Bitcoin mainnet, this means searching for a valid proof of work.

## Step 5 — Other nodes validate the block

When the miner broadcasts a block, other full nodes independently validate it.

They do not simply trust the miner's transaction selection. If the block violates consensus rules, they reject it.

If the block is valid and becomes part of the active chain, its transactions receive confirmations and the node's UTXO set is updated.

## Special case: your regtest lab

On your local regtest network, you can mine blocks on demand:

```
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

Then:

```
bitcoin-cli -regtest generatetoaddress 1 "OMAR_MINING_ADDRESS"
```

Regtest's easy, on-demand mining is useful for learning transaction validation and confirmation behavior. It does not model the competitive fee market and proof-of-work mining conditions of mainnet.

## Questions to explore next

1. What happens if a transaction remains in the mempool for several hours?
2. What is the difference between a transaction fee and a fee rate?
3. Why can a miner include an unconfirmed parent transaction and its child in the same block?
4. How does Bitcoin's proof of work make it costly to rewrite confirmed transaction history?

----------------------------------------------------------------
# Resume: What is a UTXO in Bitcoin?

UTXO = Unspent Transaction Output.

A UTXO is an output created by a Bitcoin transaction that has not yet been spent. It represents an amount of bitcoin that can potentially be spent, provided the required spending conditions are satisfied.

Let's connect everything we've learned.

## 1. How a UTXO is created

Suppose Amine receives 3 BTC from a transaction.

```
Transaction A
      |
      v
Output 0: 3 BTC
      |
      v
UTXO: 3 BTC
```

The output becomes part of the UTXO set when the transaction is incorporated into the active blockchain and its output is eligible for inclusion in that set.

The output is identified by:

```
txid + vout
```

For example, `abc123...:0` identifies output 0 of transaction `abc123...`.

## 2. What happens when Amine spends it?

Amine wants to send Sara 1 BTC. Assume a fee of 0.0001 BTC.

```
INPUT
  Amine's UTXO: 3.0000 BTC
          |
          v
     Transaction
          |
          +--------------------+
          |                    |
          v                    v
OUTPUT 0                 OUTPUT 1
Sara: 1.0000 BTC         Amine's change:
                         1.9999 BTC

Fee: 0.0001 BTC
```

The original 3 BTC output is consumed. Two new outputs are created.

- Sara's 1 BTC output becomes a UTXO.
- Amine's 1.9999 BTC change output becomes another UTXO.
- The 0.0001 BTC fee is not a separate output.

## 3. What problem does UTXO solve?

The UTXO model helps Bitcoin:

1. Prevent double spending: an already-spent output cannot be spent again in the same valid chain history.
2. Validate transactions efficiently: nodes check inputs against the current UTXO set rather than scanning the entire blockchain for every transaction.
3. Account for money transparently: transaction input values must cover output values, with the difference becoming the fee.

## 4. Where does the UTXO live?

On your Bitcoin Core node, the node-wide UTXO set is maintained in the local `chainstate` database, using LevelDB.

Default Ubuntu regtest path:

```
~/.bitcoin/regtest/chainstate/
```

Remember the distinction:

```
Blockchain = historical blocks and transactions

UTXO set   = currently unspent outputs

Wallet     = keys and transactions relevant to you
```

Your node maintains UTXOs belonging to other people too, even if their wallets are not loaded on your machine.

## 5. How to inspect UTXOs in your lab

List outputs relevant to Omar's wallet:

```
bitcoin-cli -regtest -rpcwallet=omar listunspent
```

Inspect one specific output:

```
bitcoin-cli -regtest gettxout "TXID" 0
```

Inspect statistics for the entire node's UTXO set:

```
bitcoin-cli -regtest gettxoutsetinfo
```

## The most important concept to remember

A Bitcoin transaction consumes old UTXOs and creates new outputs. Those outputs become UTXOs until another transaction spends them.

### Questions for you

1. If Amine has one UTXO worth 5 BTC and sends Sara 2 BTC, why might the transaction create a change output?
2. What happens to an old UTXO after a transaction spends it?
3. What is the difference between the UTXO set and a wallet balance?
4. Why does a Bitcoin node need LevelDB or another persistent database for its UTXO set?

----------------------------------------------------------------
# Bitcoin Script — What Is It?

Bitcoin Script is the small, stack-based programming language Bitcoin uses to define and verify the conditions for spending transaction outputs.

Remember our UTXO discussion: a UTXO is an unspent transaction output. But how does Bitcoin know whether Amine is allowed to spend it?

The answer is Bitcoin Script.

## 1. The basic idea

Suppose Amine receives 2 BTC from Sara.

When Sara creates the output, she specifies the conditions under which those 2 BTC can be spent.

Later, Amine creates a transaction spending that output. He provides the data required to satisfy those conditions, typically a digital signature and a public key.

```
Sara's transaction
        |
        v
Output: 2 BTC
        |
        v
Locking script
"What conditions must be satisfied?"
        |
        v
Amine creates a spending transaction
        |
        v
Unlocking data: signature + public key
        |
        v
Bitcoin Script verifies the conditions
        |
        v
Valid? The input may be accepted.
```

The script doesn't store the bitcoins themselves. It defines the spending conditions associated with the output.

## 2. The two important scripts

Bitcoin commonly uses two related concepts.

| Script         | Purpose                                                                        |
| -------------- | ------------------------------------------------------------------------------ |
| `scriptPubKey` | The locking script attached to an output                                       |
| `scriptSig`    | The unlocking data traditionally supplied by an input for certain script types |

For SegWit transactions, some unlocking data is provided in the transaction's witness instead of `scriptSig`.

Your Bitcoin addresses beginning with `bcrt1q` use native SegWit version 0, typically P2WPKH.

For this type, the output has a `scriptPubKey`, while the spending input normally supplies a signature and public key in its witness.

## 3. A concrete example: P2PKH

One traditional Bitcoin output type is Pay-to-Public-Key-Hash (P2PKH).

Its locking script has this structure:

```
OP_DUP
OP_HASH160
<public-key-hash>
OP_EQUALVERIFY
OP_CHECKSIG
```

What do these operations mean?

- `OP_DUP`: duplicate the public key.
- `OP_HASH160`: hash the public key using SHA-256 followed by RIPEMD-160.
- `<public-key-hash>`: the expected hash embedded in the locking script.
- `OP_EQUALVERIFY`: verify that the calculated hash matches the expected hash.
- `OP_CHECKSIG`: verify the digital signature against the public key and transaction data.

The script ensures that the spender supplies a matching public key and a valid signature.

This is a simplified explanation of the script's evaluation; the exact stack behavior matters when executing it.

## 4. What does Bitcoin Script actually execute?

Bitcoin Script uses a stack-based execution model.

Think of a stack as a pile of values. Operations push values onto it, remove values, or transform them.

For example, the following simplified script:

```
2 3 OP_ADD 5 OP_EQUAL
```

Conceptually executes as follows:

```
Push 2       Stack: [2]
Push 3       Stack: [2, 3]
OP_ADD       Stack: [5]
Push 5       Stack: [5, 5]
OP_EQUAL     Stack: [true]
```

The final result is true because \\(2+3=5\\).

This is a conceptual illustration of stack execution, not a typical payment script used in a wallet.

Bitcoin Script is intentionally limited. It is not a general-purpose language like Python, and it does not support arbitrary loops. Its restricted design helps make transaction validation predictable.

## 5. Where can you see a real script in Bitcoin Core?

You already have examples from your Omar wallet's `listunspent` output.

One of your UTXOs contained:

```
scriptPubKey: 001456c1ae942ec8dd89b8014f6e4aaf3b7ad1fbfc2d
```

This is a native SegWit version 0 locking script, using a 20-byte witness program.

You can inspect a particular output with:

```
bitcoin-cli -regtest gettxout "TXID" 0
```

Look for the `scriptPubKey` field.

To inspect a decoded transaction, use:

```
bitcoin-cli -regtest getrawtransaction "TXID" true
```

Look inside `vout` for the locking scripts. For a spending transaction, inspect `vin` and its `txinwitness` or `scriptSig` fields.

## 6. Why is Bitcoin Script important?

Bitcoin Script allows Bitcoin outputs to express conditions such as:

- A valid signature is required.
- Multiple keys must authorize spending (multisignature).
- Spending is allowed only after a specified time or block-height condition.
- Certain more complex spending conditions must be satisfied.

For your UTXO lab, the most important relationship is:

```
UTXO
 |
 +-- Amount: 2 BTC
 |
 +-- scriptPubKey: spending conditions
          |
          v
Spending transaction provides required data
          |
          v
Script and consensus validation
          |
          v
Input can be accepted if all applicable rules pass
```

Remember: a UTXO tells you which output remains unspent; Bitcoin Script defines the conditions under which that output may be spent.

## Questions to explore next

1. What is the difference between `scriptPubKey`, `scriptSig`, and `witness`?
2. How does `OP_CHECKSIG` verify a Bitcoin signature?
3. Why do your `bcrt1q` addresses use a different script structure from traditional P2PKH addresses?
4. How does a multisignature script require more than one key to authorize a spend?


# Bitcoin Script — Practical Examples

Let's look at actual Bitcoin Script examples, starting with a simple calculation and then moving to the type of script used by your Bitcoin Core wallet.

Bitcoin Script is a stack-based language. It uses instructions called opcodes to check whether a transaction satisfies the conditions for spending a UTXO.

## Example 1 — A simple script that evaluates to true

```
OP_2 OP_3 OP_ADD OP_5 OP_EQUAL
```

This is a simple demonstration script, not a real payment script.

Step by step:

Instruction

Stack after execution

`OP_2`

[2]

`OP_3`

[2, 3]

`OP_ADD`

[5]

`OP_5`

[5, 5]

`OP_EQUAL`

True

Why? Because \\(2+3=5\\). `OP_EQUAL` compares the two stack values and returns true.

## Example 2 — A real payment script: P2PKH

A traditional Pay-to-Public-Key-Hash (P2PKH) output uses this locking script:

```
OP_DUP
OP_HASH160
<PublicKeyHash>
OP_EQUALVERIFY
OP_CHECKSIG
```

Suppose Sara sends 1 BTC to an address using this output type.

The output contains the locking script. When Amine spends it, his transaction supplies a signature and public key.

Conceptually:

```
LOCKING SCRIPT (scriptPubKey)
  Check that the public key hashes correctly
  Check that the signature is valid

UNLOCKING DATA (scriptSig)
  <Signature>
  <PublicKey>
```

Bitcoin evaluates the unlocking data together with the locking script under the applicable script rules.

| Opcode           | Purpose                      |
| ---------------- | ---------------------------- |
| `OP_DUP`         | Duplicate the top stack item |
| `OP_HASH160`     | Hash the public key          |
| `OP_EQUALVERIFY` | Verify that the hashes match |
| `OP_CHECKSIG`    | Verify the signature         |

If the conditions are satisfied, the script succeeds. The transaction must still satisfy all other applicable consensus rules.

## Example 3 — The type of script used by your wallet

Your Omar wallet contains native SegWit addresses beginning with `bcrt1q`. One of your earlier outputs had this `scriptPubKey`:

```
001456c1ae942ec8dd89b8014f6e4aaf3b7ad1fbfc2d
```

This is a P2WPKH (Pay-to-Witness-Public-Key-Hash) locking script.

Its structure is:

```
00 14 <20-byte witness program>
```

- `00` identifies witness version 0.
- `14` specifies a 20-byte witness program.
- The remaining bytes are the public-key hash.

When spending this output, the transaction normally supplies the signature and public key in `txinwitness`, rather than using a traditional P2PKH `scriptSig`.

You can inspect an output on your regtest node:

```
bitcoin-cli -regtest gettxout "TXID" 0
```

Or decode a transaction:

```
bitcoin-cli -regtest getrawtransaction "TXID" true
```

Look at `vout[].scriptPubKey` for the locking script and `vin[].txinwitness` for the witness data in a native SegWit spending transaction.

## Example 4 — A script that fails

Consider:

```
OP_2 OP_3 OP_ADD OP_6 OP_EQUAL
```

The calculation is still \\(2+3=5\\), but the script compares 5 with 6.

```
Stack before OP_EQUAL: [5, 6]
Result: false
```

The script does not evaluate to true, so it fails as a spending condition.

## What you should remember

- A locking script defines the conditions for spending an output.
- The spending transaction provides data to satisfy those conditions.
- Opcodes perform operations on a stack.
- A successful script is necessary, but not sufficient by itself, for a transaction to be valid.

### Questions to explore next

1. How does `OP_CHECKSIG` verify a signature using a public key?
2. How does Bitcoin Script use a stack internally?
3. What is the difference between P2PKH and P2WPKH?
4. Can we build and test a simple custom Bitcoin Script in your regtest lab?


---------------------------------------------------------------
Yes, you've identified an important problem! This is called the trust problem in digital exchanges: how can two strangers exchange something without one person paying and the other refusing to deliver?

Bitcoin Script can help solve this problem, but ordinary Bitcoin Script alone cannot guarantee the exchange of an arbitrary image for 1 BTC. Let's see why.

## 1. The problem: who goes first?

Suppose Amine wants to buy an image from Sara for 1 BTC.

Scenario A: Amine pays first

Amine sends 1 BTC. Sara receives the payment but never sends the image.

Amine loses the money

Scenario B: Sara sends first

Sara sends the image. Amine receives it but never pays.

Sara loses the sale

Bitcoin transactions can enforce conditions on spending bitcoins, but Bitcoin cannot inherently determine whether Sara has actually delivered an image or whether Amine is satisfied with it.

## 2. Can Bitcoin Script solve it?

Bitcoin Script can lock bitcoins under specific conditions. For example, Amine can create a transaction that locks 1 BTC so that it can be claimed only by a specified key, or under a more complex set of conditions.

But a basic script cannot say:

```
IF Sara really sent the image:
    pay Sara 1 BTC
ELSE:
    refund Amine
```

Why not? The Bitcoin blockchain does not automatically know whether an image was sent over email, uploaded to a website, or delivered privately.

This is an information problem: the blockchain can verify cryptographic conditions, but it cannot directly verify arbitrary off-chain events.

## 3. A better approach: escrow with a third party

One practical solution is to use a trusted escrow service or an arbitrator.

```
             Amine deposits 1 BTC
                      |
                      v
                 ESCROW
                      |
              +-------+-------+
              |               |
              v               v
       Sara delivers      Amine confirms
          image             receipt
              |               |
              +-------+-------+
                      |
                      v
                Release payment
```

The escrow service holds the funds until the agreed conditions are met. If there is a dispute, an arbitrator can decide what happens.

This introduces a trusted party, so it does not eliminate trust entirely.

Bitcoin's multisignature scripts can help implement certain escrow arrangements. For example, a 2-of-3 multisignature arrangement can require two of three keys to authorize a payment: Amine's, Sara's, and an arbitrator's. The precise design determines how refunds and disputes work.

## 4. A more advanced approach: cryptographic commitments and hashlocks

Bitcoin Script also supports hash-based conditions. These can help coordinate exchanges when both parties can prepare cryptographically linked transactions.

For example, a hashlock can require someone to reveal a secret whose hash matches a specified value. A timeout can provide a refund path if the exchange does not complete.

This is useful for certain atomic swaps and other protocols, but a hashlock does not prove that an image was delivered. It only proves that the required secret was revealed.

To connect payment to digital delivery, a protocol might use encryption, a secret key, and a carefully designed refund mechanism. Even then, the protocol must account for whether the buyer can decrypt and use the file, whether the seller can withhold the key, and whether the file is actually what was promised.

## 5. The key distinction

| Mechanism                    | What it can enforce                                                |
| ---------------------------- | ------------------------------------------------------------------ |
| Ordinary Bitcoin transaction | Transfers bitcoin under valid spending conditions                  |
| Bitcoin Script               | Enforces supported cryptographic and transaction conditions        |
| Multisignature escrow        | Requires multiple keys to authorize spending                       |
| Hashlock and timeout         | Coordinates certain cryptographic exchanges with refund conditions |
| Arbitrator or escrow service | Can assess an off-chain dispute, subject to its trustworthiness    |

The fundamental lesson: Bitcoin Script can enforce payment rules, but it cannot independently verify that an arbitrary real-world or digital action has occurred.

### Questions you can explore next

1. How does a Bitcoin hashlock work, with a concrete example?
2. How can a 2-of-3 multisignature escrow work in your regtest lab?
3. Can we design an exchange where neither person has to trust the other to act honestly?
4. What is an atomic swap, and how does it differ from ordinary escrow?


# Summary — Bitcoin Script

## 1. What is Bitcoin Script?

Bitcoin Script is a stack-based programming language that defines and verifies the conditions for spending Bitcoin transaction outputs.

When someone sends you bitcoin, the transaction creates an output with a locking script. When you want to spend that output, your transaction must provide the data needed to satisfy the script's conditions.

## 2. How does it work?

```
Transaction creates an output
            |
            v
        UTXO created
            |
            v
   scriptPubKey (locking script)
   Defines spending conditions
            |
            v
   Someone tries to spend the UTXO
            |
            v
   Supplies signature / required data
            |
            v
   Bitcoin Script evaluates conditions
            |
            v
   Script succeeds? Continue validation
```

A successful script is necessary, but the transaction must also satisfy the other Bitcoin consensus rules.

## 3. The important components

| Component      | Meaning                                                  |
| -------------- | -------------------------------------------------------- |
| `scriptPubKey` | Locking script attached to an output                     |
| `scriptSig`    | Unlocking data used by certain traditional script types  |
| `witness`      | Separate transaction data used by SegWit spending        |
| Opcode         | An instruction executed by Bitcoin Script                |
| Stack          | Structure used to process values during script execution |

Your `bcrt1q...` regtest addresses generally use native SegWit P2WPKH outputs, whose spending data is provided in the witness.

## 4. Example of Bitcoin Script

A simple demonstration script:

```
OP_2 OP_3 OP_ADD OP_5 OP_EQUAL
```

Execution:

```
Push 2       → [2]
Push 3       → [2, 3]
OP_ADD       → [5]
Push 5       → [5, 5]
OP_EQUAL     → [true]
```

The script succeeds because \\(2+3=5\\).

A traditional P2PKH payment script uses:

```
OP_DUP
OP_HASH160
<PublicKeyHash>
OP_EQUALVERIFY
OP_CHECKSIG
```

This checks that the public key matches the expected hash and that the signature is valid.

## 5. What problems does Bitcoin Script solve?

Bitcoin Script allows Bitcoin outputs to enforce conditions such as:

- Requiring a valid digital signature.
- Requiring multiple keys to authorize spending.
- Enforcing certain time or block-height conditions.
- Supporting hashlocks used in some cryptographic exchange protocols.

However, Script cannot directly verify arbitrary off-chain events, such as whether someone emailed an image to another person.

## 6. Where does Script fit into your Bitcoin Core node?

```
Transaction input
      |
      v
References a UTXO
      |
      v
Bitcoin Core finds the previous output
      |
      v
Evaluates its spending conditions
      |
      v
Checks the remaining transaction rules
      |
      v
Transaction accepted or rejected
```

Bitcoin Core implements the script interpreter and transaction-validation rules. The UTXO's locking script specifies the conditions that must be met.

## 7. Commands to inspect scripts in your regtest lab

Inspect an output:

```
bitcoin-cli -regtest gettxout "TXID" 0
```

Decode a transaction:

```
bitcoin-cli -regtest getrawtransaction "TXID" true
```

Look at `vout[].scriptPubKey` for the locking script and `vin[].txinwitness` or `vin[].scriptSig` for the spending data.

## Key takeaway

UTXO tells you which output remains unspent. Bitcoin Script defines the conditions for spending it. Bitcoin Core evaluates those conditions when validating a transaction.

### Questions for your next step

1. How does `OP_CHECKSIG` verify a digital signature?
2. What is the difference between P2PKH and P2WPKH?
3. How does a 2-of-3 multisignature script work?
4. How can you create and test a simple custom Bitcoin Script in your regtest lab?