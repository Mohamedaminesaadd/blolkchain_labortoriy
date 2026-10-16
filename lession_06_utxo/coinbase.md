# Lab 19, 20, 21 — Regtest Mining, Coinbase Transactions & Maturity

These three labs are connected. You will make Omar the miner, investigate the Bitcoin transaction created when he mines a block, and understand why newly mined bitcoins cannot be spent immediately.

Everything takes place on your local Bitcoin Core `regtest` network, so you can mine blocks on demand without using real bitcoins.

# Lab 19 — First Regtest Mining Operation

## 1. Objective

Understand how a Bitcoin node creates blocks, how a miner receives a reward, and how `generatetoaddress` works.

The basic process is:

```
OMAR (Bitcoin node)
       |
       v
Choose a receiving address
       |
       v
Generate a block
       |
       v
Block added to the regtest blockchain
       |
       v
Coinbase transaction created
       |
       v
Mining reward recorded as a UTXO
```

In this lab, Omar acts as the miner. On `regtest`, Bitcoin Core lets you generate blocks immediately using a command.

## 2. Check the current blockchain height

Open Omar's terminal and run:

```
bitcoin-cli -regtest getblockchaininfo
```

Look for these fields:

```
{
  "chain": "regtest",
  "blocks": 103,
  "bestblockhash": "..."
}
```

The values above are illustrative. Your actual block height may be different.

- `chain`: confirms the network is `regtest`.
- `blocks`: current height of the active blockchain.
- `bestblockhash`: hash of the latest block in the active chain.

Record the height before mining. Suppose it is 103.

## 3. Generate a mining address for Omar

Run:

```
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

Example:

```
bcrt1qexample...
```

Use the actual address returned by Bitcoin Core. This address specifies where the coinbase transaction's mining reward will be paid.

## 4. Mine one block

Copy Omar's actual address and execute:

```
bitcoin-cli -regtest generatetoaddress 1 "OMAR_MINING_ADDRESS"
```

Replace `OMAR_MINING_ADDRESS` with the address from the previous step.

The number `1` means generate one block.

The result is a list containing the hash of the newly generated block:

```
[
  "new_block_hash"
]
```

Bitcoin Core creates the block and adds it to the active regtest chain.

## 5. Verify the result

```
bitcoin-cli -regtest getblockchaininfo
```

If the previous height was 103 and the block was successfully generated, the new height should be 104.

You can also inspect the block:

```
bitcoin-cli -regtest getblock "NEW_BLOCK_HASH" 2
```

Replace `NEW_BLOCK_HASH` with the hash returned by `generatetoaddress`.

The `2` requests decoded transaction details, including the coinbase transaction.

Important: Generating a block is not the same as receiving immediately spendable bitcoins. The coinbase reward has a maturity requirement, which you will investigate in Lab 21.

# Lab 20 — Coinbase Transaction

## 1. What is a coinbase transaction?

A coinbase transaction is the special first transaction in a mined Bitcoin block. It creates the block's reward for the miner.

The term coinbase here is a Bitcoin protocol term. It is not the name of a cryptocurrency exchange.

The flow is:

```
Omar mines a block
       |
       v
Block contains a coinbase transaction
       |
       v
Coinbase transaction creates an output
       |
       v
Output is locked to Omar's mining address
       |
       v
Output becomes a UTXO
       |
       v
UTXO becomes spendable after maturity
```

A coinbase transaction differs from a normal transaction because it has no ordinary spending input. Its input contains special data associated with the block.

## 2. Find the coinbase transaction

First, obtain the latest block hash:

```
bitcoin-cli -regtest getbestblockhash
```

Inspect that block:

```
bitcoin-cli -regtest getblock "BLOCK_HASH" 2
```

Replace `BLOCK_HASH` with the actual hash returned by the previous command.

In the decoded block output, look at the `tx` array. The first transaction is the coinbase transaction.

It will look conceptually like this:

```
{
  "txid": "coinbase_transaction_id",
  "vin": [
    {
      "coinbase": "..."
    }
  ],
  "vout": [
    {
      "value": 50.00000000,
      "scriptPubKey": {
        "address": "OMAR_MINING_ADDRESS"
      }
    }
  ]
}
```

This is an illustrative structure; your actual output may contain additional fields or different values.

### Understand the fields

- `txid`: identifier of the coinbase transaction.
- `vin`: transaction inputs. The `coinbase` field identifies the special coinbase input.
- `vout`: outputs created by the transaction.
- `value`: amount assigned to the output, denominated in BTC.
- `scriptPubKey`: spending conditions for the output.

On regtest, the initial block subsidy is 50 BTC. The subsidy halves every 150 blocks on regtest, rather than every 210,000 blocks as on mainnet. The coinbase transaction may also claim transaction fees from the block, so the total reward can include both the subsidy and eligible fees.

## 3. Find the resulting UTXO

Run:

```
bitcoin-cli -regtest -rpcwallet=omar listunspent 0
```

The `0` allows outputs with zero confirmations to appear in the result, subject to the other default filters.

Find the entry corresponding to the mining address and transaction you just inspected.

You may see fields such as:

```
{
  "txid": "coinbase_transaction_id",
  "vout": 0,
  "address": "OMAR_MINING_ADDRESS",
  "amount": 50.00000000,
  "confirmations": 1,
  "spendable": false
}
```

The example is illustrative. Actual fields and spendability can differ.

The output is now recorded in the blockchain, but the wallet should not allow it to be spent before coinbase maturity.

## 4. Why is it a UTXO?

A coinbase transaction creates an output, and that output remains unspent until a later transaction consumes it.

A UTXO is not the same thing as a wallet balance:

- A UTXO represents one individual unspent output.
- A wallet balance is calculated from multiple outputs, subject to confirmation, maturity, and wallet accounting rules.

For example, Omar could have three UTXOs worth 50 BTC, 3 BTC, and 1.2 BTC. Those outputs are tracked separately even though they belong to the same wallet.

# Lab 21 — Coinbase Maturity

## 1. What does maturity mean?

Bitcoin requires a newly mined coinbase output to reach 100 confirmations before it can be spent.

For a coinbase output:

- At 1 confirmation: not spendable.
- At 10 confirmations: not spendable.
- At 99 confirmations: not spendable.
- At 100 confirmations: mature and potentially spendable, assuming all other requirements are satisfied.

The 100-confirmation rule is a consensus rule, not just a user-interface setting.

## 2. Why does Bitcoin have this rule?

Coinbase maturity reduces the risk of a miner spending newly created coins from a block that is later removed from the active chain during a chain reorganization.

If a block is reorganized out of the active chain, its coinbase reward is invalidated along with that block's other effects. The maturity delay reduces the chance that the reward has already been spent before the chain has had time to develop.

## 3. Experiment with 1, 10, 100, and 101 blocks

There is one important detail: the relevant value is the coinbase output's confirmation count, not simply how many blocks you generate after the mining transaction.

Suppose Omar generates a block at height 104. Its coinbase output initially has one confirmation.

If you generate 99 additional blocks, that output reaches 100 confirmations. Generating 100 additional blocks would bring it to 101 confirmations.

You can verify this in a controlled experiment.

### Step 1 — Start with a fresh coinbase output

Record the current height:

```
bitcoin-cli -regtest getblockcount
```

Generate a new address:

```
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

Mine one block to that address:

```
bitcoin-cli -regtest generatetoaddress 1 "OMAR_MINING_ADDRESS"
```

Find the coinbase transaction in the new block, then locate its output using:

```
bitcoin-cli -regtest -rpcwallet=omar listunspent 0
```

Record its `txid`, `vout`, and `confirmations`.

### Step 2 — Observe the output at 1 confirmation

Immediately after the block is mined, the coinbase output should have one confirmation.

You can inspect its current state:

```
bitcoin-cli -regtest -rpcwallet=omar listunspent 0
```

Depending on the wallet's filters and output details, immature coinbase outputs may be omitted or reported as not spendable. You can also inspect the wallet's immature balance:

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

Look for `mine.immature`.

### Step 3 — Generate 9 additional blocks

Use the same mining address:

```
bitcoin-cli -regtest generatetoaddress 9 "OMAR_MINING_ADDRESS"
```

The original coinbase output should now have 10 confirmations.

Check again:

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

The original coinbase output remains immature.

### Step 4 — Reach 100 confirmations

If the output currently has 10 confirmations, mine 90 more blocks:

```
bitcoin-cli -regtest generatetoaddress 90 "OMAR_MINING_ADDRESS"
```

The original coinbase output should now have 100 confirmations.

Check the wallet state:

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

At this point, the output can become spendable if it is still unspent and the wallet has the necessary keys.

### Step 5 — Generate one more block

```
bitcoin-cli -regtest generatetoaddress 1 "OMAR_MINING_ADDRESS"
```

The original output should now have 101 confirmations.

Why does the lab include 101? It lets you observe the state after the output has crossed the maturity threshold, rather than only at the exact boundary.

## 4. Confirmation table

Assume the coinbase output has just been created in a mined block.

| Blocks generated after its creation | Coinbase confirmations | Mature?               |
| ----------------------------------- | ---------------------- | --------------------- |
| 0 additional blocks                 | 1                      | No                    |
| 9 additional blocks                 | 10                     | No                    |
| 98 additional blocks                | 99                     | No                    |
| 99 additional blocks                | 100                    | Yes, maturity reached |
| 100 additional blocks               | 101                    | Yes                   |

The count includes the block containing the coinbase transaction. That is why 99 additional blocks after the original block produce 100 confirmations.

## 5. Important distinction: maturity versus wallet balance

The following are not equivalent:

- Total balance: all coins the wallet accounts for.
- Immature balance: coinbase rewards that have not yet reached maturity.
- Spendable balance: coins the wallet can currently use in a transaction.

Use:

```
bitcoin-cli -regtest -rpcwallet=omar getbalances
```

A wallet might show a positive immature balance even when those coins cannot be spent.

Also, mining each new block creates another coinbase reward for the mining address. Those new rewards begin their own maturity countdown. When you mine many blocks, you are maturing older coinbase rewards while creating new immature ones.

# Final lab exercise

Complete the following checklist:

- Generate an address for Omar.
- Mine one block using `generatetoaddress`.
- Identify the coinbase transaction in that block.
- Identify its output and corresponding UTXO.
- Observe the coinbase output at 1 and 10 confirmations.
- Reach 100 confirmations and check whether the output is spendable.
- Mine one more block and observe 101 confirmations.
- Compare `mine.immature` and `mine.trusted` in `getbalances`.

## Knowledge check

1. What is the difference between a coinbase transaction and a normal Bitcoin transaction?
2. Why does a coinbase output require 100 confirmations before it can be spent?
3. If a coinbase output has 1 confirmation, how many additional blocks are needed to reach 100 confirmations?
4. If Omar mines 101 blocks in a row, are all 101 coinbase rewards mature? Explain.
5. What is the differeence between a block reward, a coinbase transaction, and a UTXO?