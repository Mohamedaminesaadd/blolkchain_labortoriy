Here is your Sara wallet's UTXO output formatted as valid JSON, ready to save in your Markdown lab notes.

```

{
  "wallet": "sara",
  "network": "regtest",
  "utxos": [
    {
      "txid": "e2f0076715b2fa6bd842f2bf2fda2dacc33ea88fafc09172eaaafa0b186ec6cf",
      "vout": 0,
      "address": "bcrt1qgf7j0t378sk3x42csazysj9hzek0kfpuu0uawy",
      "scriptPubKey": "0014427d27ae3e3c2d13555887444848b7166cfb243c",
      "amount": 0.99999859,
      "confirmations": 6,
      "spendable": true,
      "solvable": true,
      "safe": true
    },
    {
      "txid": "ad96aa0449defa5dc2955aa43aa51c5005a0217479b98a1a535ffe04eada0508",
      "vout": 1,
      "address": "bcrt1qzxkml4yqfk006wqpj0js3kj6lwya95l3pqax7a",
      "label": "Native SegWit",
      "scriptPubKey": "001411adbfd4804d9efd380193e508da5afb89d2d3f1",
      "amount": 1.0,
      "confirmations": 5,
      "spendable": true,
      "solvable": true,
      "safe": true
    }
  ],
  "summary": {
    "utxo_count": 2,
    "total_balance_btc": 1.99999859
  }
}

```

## Interpretation

- Number of UTXOs: 2
- Total value: 1.99999859 BTC
- First UTXO: 0.99999859 BTC, with 6 confirmations.
- Second UTXO: 1.0 BTC, with 5 confirmations.
- Both outputs are marked `spendable: true`.

The total is the sum of the two outputs shown, not necessarily Sara's entire wallet balance if other UTXOs were excluded by the command.

For your Markdown lab, you can keep the raw JSON under a heading such as `## Sara wallet — UTXO inspection`. I omitted the `desc` and `parent_descs` fields to keep this capture concise; the original output contains them if you need the complete RPC response.
----------------------------------------------------------------
# Understanding Sara's UTXOs in your Bitcoin Regtest lab

Your command:

```
bitcoin-cli -regtest -rpcwallet=sara listunspent
```

returned 2 UTXOs. This means Sara's wallet knows about two unspent transaction outputs that it can currently spend.

## 1. Overview of Sara's UTXOs

Total value of these UTXOs

# 1.99999859 BTC

UTXO 1

Output index: 0

## 0.99999859 BTC

6 confirmations

UTXO 2

Output index: 1

## 1.00000000 BTC

5 confirmations

These are two separate outputs created by two transactions. They are not necessarily two separate payments from two different people; we need to inspect the transactions to determine their origin.

## 2. Explanation of every important field

Let's examine the first UTXO.

TRANSACTION ID (TXID)

e2f0076715b2fa6bd842f2bf2fda2dacc33ea88fafc09172eaaafa0b186ec6cf

OUTPUT INDEX (VOUT)

0

Identifies output number 0 within that transaction. Together, txid and vout uniquely identify this UTXO.

AMOUNT

## 0.99999859 BTC

The value assigned to this output.

ADDRESS

bcrt1qgf7j0t378sk3x42csazysj9hzek0kfpuu0uawy

A regtest address associated with this output. The address itself is not the UTXO's unique identifier.

Here is what the remaining fields mean:

| Field             | Meaning                                                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `scriptPubKey`    | The locking script that defines the conditions required to spend the output.                                                  |
| `confirmations`   | Number of blocks confirming the transaction, as reported by the node.                                                         |
| `spendable: true` | Sara's wallet considers the output spendable with its available keys and wallet state.                                        |
| `solvable: true`  | The wallet knows how the output could be spent, though solvability alone does not guarantee it has the necessary private key. |
| `safe: true`      | Bitcoin Core considers the output safe to use for spending according to its wallet safety rules.                              |
| `label`           | Optional wallet metadata attached to the address.                                                                             |
| `desc`            | Descriptor describing how the wallet derives or recognizes the output's spending conditions.                                  |
| `parent_descs`    | Descriptors associated with the parent output's derivation path.                                                              |

The second UTXO has the same types of fields, but its `txid`, `vout`, address, value, and confirmation count are different.

## 3. What is `scriptPubKey`?

For the first UTXO, you have:

```
0014427d27ae3e3c2d13555887444848b7166cfb243c
```

This is a locking script in serialized form.

Your output uses the native SegWit P2WPKH format, as indicated by its address and descriptor `wpkh(...)`.

The script can be interpreted as:

- `00`: SegWit version 0.
- `14`: the following data is 20 bytes long, written in hexadecimal as 40 characters.
- `427d27ae3e3c2d13555887444848b7166cfb243c`: the 20-byte witness program, which is a hash associated with the public key.

In simple terms, this output can normally be spent by providing a valid signature and public key that satisfy the output's conditions.

The second output also uses native SegWit P2WPKH.

## 4. Why do the outputs have 6 and 5 confirmations?

A confirmation means a block has included the transaction.

For example, if the transaction containing Sara's first UTXO is included in a block, it has one confirmation. Each subsequent block adds another confirmation.

Your outputs have 6 and 5 confirmations, respectively. This means the transactions were included at different heights, assuming both are confirmed on the same active chain.

In your regtest environment, you control block production, so you can mine blocks yourself.

## 5. How to inspect where each UTXO came from

This is the next useful step in your lab. Run:

```
bitcoin-cli -regtest getrawtransaction \
  e2f0076715b2fa6bd842f2bf2fda2dacc33ea88fafc09172eaaafa0b186ec6cf true
```

Then inspect the second transaction:

```
bitcoin-cli -regtest getrawtransaction \
  ad96aa0449defa5dc2955aa43aa51c5005a0217479b98a1a535ffe04eada0508 true
```

If Bitcoin Core cannot retrieve a transaction by txid, it may be necessary to specify the block hash or use a wallet RPC, depending on the transaction and node configuration.

In the decoded transaction, look at:

- `vin`: the previous outputs consumed as inputs.
- `vout`: the new outputs created by the transaction.
- `scriptPubKey`: the locking conditions for each output.
- `value`: the BTC amount of each output.

The key concept: your UTXO is an output of a transaction, not an entire transaction. To understand its history, inspect the transaction that created it and, if needed, trace the previous outputs consumed by that transaction.
--------------------------------------------------------------
Here is the decoded transaction intercepted from your Bitcoin Core `regtest` lab, formatted as JSON for your Markdown notes, followed by an explanation of its inputs and outputs.

## 1. Transaction JSON

```

{
  "network": "regtest",
  "transaction": {
    "txid": "ad96aa0449defa5dc2955aa43aa51c5005a0217479b98a1a535ffe04eada0508",
    "hash": "c5658b84725cccfbd62bb3c6cea419fffca801035ff0808cf06a4d4c14957091",
    "version": 2,
    "size": 222,
    "vsize": 141,
    "weight": 561,
    "locktime": 0,
    "confirmations": 5,
    "blockhash": "1112fab8d459c3d89d2ca17da4e6a37502bc200d5a9966c5c9cefd912da31c83",
    "time": 1791720256,
    "blocktime": 1791720256,
    "inputs": [
      {
        "previous_txid": "5a8d20808236f6b3c7e4ff27c11ba0ca77ca3560ffeda3b04f25b1d5a538f8f7",
        "previous_vout": 1,
        "scriptSig": "",
        "witness": [
          "3044022039afce172e27fa25c109ede7c0e4952513a2e939137559e8e168f0f5a59c880702201f9a7820b7052d376b13c0ee7f00fee38a339209458892f808a1ff3235ebe38701",
          "02d7b5c00fc656a623c7da86f71689ca4b69ce381f8836452ffb0edef6cd8d7900"
        ],
        "sequence": 4294967293
      }
    ],
    "outputs": [
      {
        "vout": 0,
        "amount_btc": 43.99999577,
        "address": "bcrt1qel2z05922drhazn89tm6q84wcctars89hu7lxg",
        "script_type": "witness_v0_keyhash",
        "scriptPubKey": "0014cfd427d0aa53477e8a672af7a01eaec617d1c0e5"
      },
      {
        "vout": 1,
        "amount_btc": 1.0,
        "address": "bcrt1qzxkml4yqfk006wqpj0js3kj6lwya95l3pqax7a",
        "script_type": "witness_v0_keyhash",
        "scriptPubKey": "001411adbfd4804d9efd380193e508da5afb89d2d3f1"
      }
    ],
    "fee_btc": null,
    "raw_hex": "02000000000101f7f838a5d5b1254fb0a3edff6035ca77caa01bc127ffe4c7b3f6368280208d5a0100000000fdffffff0259aa420601000000160014cfd427d0aa53477e8a672af7a01eaec617d1c0e500e1f5050000000016001411adbfd4804d9efd380193e508da5afb89d2d3f102473044022039afce172e27fa25c109ede7c0e4952513a2e939137559e8e168f0f5a59c880702201f9a7820b7052d376b13c0ee7f00fee38a339209458892f808a1ff3235ebe387012102d7b5c00fc656a623c7da86f71689ca4b69ce381f8836452ffb0edef6cd8d790000000000"
  }
}

```

Note: `fee_btc` is `null` because the input value is not included in this decoded response. The JSON above preserves the important transaction data while renaming `vin` and `vout` to make the structure easier to understand.

## 2. What happened in this transaction?

Previous transaction output spent

TXID: `5a8d2080...a538f8f7`

## Output index 1

The input consumed by this transaction

New outputs created

Output 0

`bcrt1qel2z...`

### 43.99999577 BTC

Output 1 — Sara's UTXO

`bcrt1qzxkml...`

### 1.00000000 BTC

### Important observations

- One input: the transaction spends output `1` from the previous transaction.
- Two outputs: output `0` contains 43.99999577 BTC, and output `1` contains 1 BTC.
- Sara's UTXO: output `1` matches the second UTXO in your earlier `listunspent` result because both have the same transaction ID, output index, address, and amount.
- Five confirmations: the transaction has been included in a block and has five confirmations according to your node.

The 43.99999577 BTC output may be change returned to the sender, but the transaction alone does not prove who owns that address.

## 3. How to find the previous input value

Run:

```
bitcoin-cli -regtest getrawtransaction \
  5a8d20808236f6b3c7e4ff27c11ba0ca77ca3560ffeda3b04f25b1d5a538f8f7 true
```

Find the value of output `1` in that transaction. Then calculate:

\\[ \text{Fee}=\text{Input value}-(43.99999577+1.00000000) \\]

The two outputs total 44.99999577 BTC. Once you know the previous output's value, you can calculate the exact transaction fee.
---------------------------------------------------------
# Bitcoin Regtest Lab — Tracing the UTXO history

Your latest command reveals the previous transaction that created the input used by Sara's 1 BTC UTXO. We can now trace the chain of transactions backward.

## 1. Decoded transaction in JSON

Save this in your Markdown lab notes as `previous_transaction.json`.

```

{
  "network": "regtest",
  "transaction": {
    "txid": "5a8d20808236f6b3c7e4ff27c11ba0ca77ca3560ffeda3b04f25b1d5a538f8f7",
    "hash": "520b9afc489aa440761c3007ec7b33cb338aec638768365ce556b441906a24bd",
    "version": 2,
    "size": 222,
    "vsize": 141,
    "weight": 561,
    "locktime": 102,
    "confirmations": 6,
    "blockhash": "2c10e73d2eeb5b8856c31ca27a5def38b52616c899fad26812a8bd04974cba9d",
    "inputs": [
      {
        "previous_txid": "da1991b7034a929cf5f4654716cabf7554360b9e3eba1773891c9f8e5f4ba34c",
        "previous_vout": 1,
        "sequence": 4294967293,
        "scriptSig": "",
        "witness": [
          "3044022007a5bba2ef5e923b6331e92fe1a461b3c157b859147dc13048e1b3147e62eb5002204b1816822d15f730e9152a0d714ecfac868c5064924ca625815448a78a9fee3001",
          "03bdf7a35b45201bb461b29f4b80e6f7e899dafc25788e629dbbd386ea04c5cd45"
        ]
      }
    ],
    "outputs": [
      {
        "vout": 0,
        "amount_btc": 3.0,
        "address": "bcrt1qn25rtxwz0wduv0rt0rcrp0qmmg33cqva6ytugn",
        "script_type": "witness_v0_keyhash",
        "scriptPubKey": "00149aa83599c27b9bc63c6b78f030bc1bda231c019d"
      },
      {
        "vout": 1,
        "amount_btc": 44.99999718,
        "address": "bcrt1qwdxpmeumqysp2txw6pguvhkxg9ra6l6fsnt9qe",
        "script_type": "witness_v0_keyhash",
        "scriptPubKey": "0014734c1de79b0120152cced051ec64147dd7f49"
      }
    ],
    "raw_hex": "020000000001014ca34b5f8e9f1c897317ba3e9e0b365475bfca164765f4f59c924a03b79119da0100000000fdffffff0200a3e111000000001600149aa83599c27b9bc63c6b78f030bc1bda231c019de68b380c01000000160014734c1de79b0120152cced051c65ec64147dd7f4902473044022007a5bba2ef5e923b6331e92fe1a461b3c157b859147dc13048e1b3147e62eb5002204b1816822d15f730e9152a0d714ecfac868c5064924ca625815448a78a9fee30012103bdf7a35b45201bb461b29f4b80e6f7e899dafc25788e629dbbd386ea04c5cd4566000000"
  }
}

```

Note: I normalized the structure for your notes. The `scriptPubKey` for output 1 should be copied exactly from your terminal if you need byte-for-byte fidelity.

## 2. What does this transaction tell us?

This transaction has one input and two outputs.

| Component     | Value           | Meaning                                        |
| ------------- | --------------- | ---------------------------------------------- |
| Input         | Not yet known   | Spends output 1 from transaction `da1991b7...` |
| Output 0      | 3.00000000 BTC  | Sent to address `bcrt1qn25...`                 |
| Output 1      | 44.99999718 BTC | Sent to address `bcrt1qwdx...`                 |
| Total outputs | 47.99999718 BTC | Sum of both outputs                            |

We cannot calculate this transaction's exact fee yet because we still need the value of its input.

## 3. Trace the transaction chain

You have now traced Sara's 1 BTC UTXO back to the transaction that created its parent output.

Transaction A

`da1991b7...` — not inspected yet

Contains the input for Transaction B

Transaction B

`5a8d2080...`

### Output 1: 44.99999718 BTC

This output is spent by Transaction C

Transaction C

`ad96aa04...`

### Output 1: 1 BTC

Sara's UTXO — 5 confirmations

Notice that Transaction B's output of `44.99999718 BTC` is not itself Sara's current UTXO anymore. Transaction C spent that output and created a new 1 BTC output for Sara, plus another output of `43.99999577 BTC`.

The difference is the transaction fee:

\\[ 44.99999718-1.00000000-43.99999577 =0.00000141\ \text{BTC} \\]

So Transaction C paid a fee of 0.00000141 BTC, or 141 satoshis.

## 4. Your next interception command

To continue tracing backward, inspect Transaction A:

```
bitcoin-cli -regtest getrawtransaction \
  da1991b7034a929cf5f4654716cabf7554360b9e3eba1773891c9f8e5f4ba34c true
```

Find the value of its output with `"n": 1`. That value is the input value for Transaction B. Then we can calculate Transaction B's fee and continue tracing its history.
----------------------------------------------------------
# Difference between `vin` and `vout` in Bitcoin

In a Bitcoin transaction:

- `vin` = transaction inputs: existing UTXOs that the transaction spends.
- `vout` = transaction outputs: new outputs that the transaction creates.

Think of it like spending a banknote: `vin` is the money you use, and `vout` is how that money is distributed to recipients and returned as change.

## 1. Example from your Regtest lab

Your transaction `ad96aa04...` has this structure:

`vin` — Input

Previous transaction: `5a8d2080...`

Previous output index

## `vout: 1`

This input spends the previous output worth 44.99999718 BTC.

New transaction

`vout` — Outputs

Output 0

### 43.99999577 BTC

Output 1 — Sara

### 1.00000000 BTC

Total outputs: 44.99999577 BTC

Transaction fee

## 141 sats

## 2. What does each field contain?

| Field                 | Meaning                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| `vin[].txid`          | ID of the previous transaction                                                                   |
| `vin[].vout`          | Index of the previous output being spent                                                         |
| `vin[].txinwitness`   | Signature and public-key data used to satisfy the spending conditions in this SegWit transaction |
| `vout[].n`            | Index of the new output                                                                          |
| `vout[].value`        | Amount assigned to the new output                                                                |
| `vout[].scriptPubKey` | Conditions for spending the new output                                                           |

Important: `vin[].vout` and `vout[].n` are not the same thing. The first points to an output of an older transaction; the second identifies an output of the current transaction.

## 3. The rule to remember

\\[ \text{Total Inputs}=\text{Total Outputs}+\text{Transaction Fee} \\]

A transaction consumes existing outputs through `vin` and creates new outputs through `vout`.

An output can become a UTXO after it is created, provided it remains unspent. When a later transaction uses that output as an input, it is no longer an unspent output.

In your lab, use:

```
bitcoin-cli -regtest getrawtransaction TXID true
```

Inspect `vin` to trace the transaction's history backward, and inspect `vout` to see where the transaction's funds went.


----------------------------------------------------------------
# Lab 23 — UTXO Lifecycle

Objective: Understand how a Bitcoin UTXO is created, becomes available, gets selected as a transaction input, is spent, disappears from the UTXO set, and is replaced by new outputs.

We'll use your existing Bitcoin Core `regtest` lab with three wallets:

- `amine` — sender
- `sara` — recipient
- `omar` — miner

## 1. Understand the lifecycle

Your lifecycle diagram is correct conceptually, with one important distinction: a spent UTXO is removed from the current UTXO set, but its historical transaction output remains recorded in the blockchain.

1\. UTXO created

A transaction creates an output in `vout`.

2\. UTXO available

It is unspent and may be recognized as spendable by a wallet.

3\. UTXO selected

The wallet chooses it as an input for a new transaction.

4\. UTXO spent

The spending transaction consumes the previous outpoint.

5\. Removed from the UTXO set

The old output is no longer available to spend.

6\. New UTXOs created

The new transaction creates payment and possibly change outputs.

The key technical terms are:

- Outpoint: the combination of a transaction ID (`txid`) and output index (`vout`).
- UTXO set: all currently unspent transaction outputs maintained by a fully validating Bitcoin node.
- Mempool: the node's pool of unconfirmed transactions. A transaction in the mempool may already spend an output that the wallet previously showed as unspent.
- Change output: the portion of the input value returned to the sender when the payment does not consume the entire input.

## 2. Experiment A — Create a new UTXO

First, inspect Sara's current UTXOs on the Sara node:

```
bitcoin-cli -regtest -rpcwallet=sara listunspent
```

You previously found these two outputs:

| Outpoint          | Amount         | Confirmations |
| ----------------- | -------------- | ------------- |
| `e2f007...ec6f:0` | 0.99999859 BTC | 6             |
| `ad96aa...0508:1` | 1.00000000 BTC | 5             |

These are your starting observations. The confirmation counts may have changed since your earlier command.

Now generate a fresh address for Sara:

```
bitcoin-cli -regtest -rpcwallet=sara getnewaddress
```

Save the returned address. For this experiment, Sara will send 0.1 BTC to that address from her own wallet, creating a new payment output and potentially a change output.

```
SARA_ADDRESS=$(bitcoin-cli -regtest -rpcwallet=sara getnewaddress)

TXID=$(bitcoin-cli -regtest -rpcwallet=sara \
  sendtoaddress "$SARA_ADDRESS" 0.1)

echo "$TXID"
```

Save the transaction ID in your notes.

## 3. Experiment B — Observe the UTXO before confirmation

On Sara's node, inspect the new transaction:

```
bitcoin-cli -regtest getrawtransaction "$TXID" true
```

Check its outputs:

```
{
  "vout": [
    {
      "value": 0.1,
      "n": 0
    }
  ]
}
```

This is an illustrative excerpt; the actual output indexes and values depend on the transaction.

Now inspect Sara's UTXOs:

```
bitcoin-cli -regtest -rpcwallet=sara listunspent 0
```

The `0` means include outputs with zero confirmations.

You may see the new output before it is mined. Meanwhile, the input selected by the wallet may no longer be available for another spend because the transaction is in the mempool.

Check the original output directly:

```
bitcoin-cli -regtest gettxout \
  ad96aa0449defa5dc2955aa43aa51c5005a0217479b98a1a535ffe04eada0508 \
  1
```

If this particular output was selected as the input, `gettxout` will normally return `null` while the spending transaction is in the mempool, because the RPC includes mempool spends by default. If another UTXO was selected, inspect that input's outpoint instead.

## 4. Experiment C — Confirm the transaction

On Omar's miner node, confirm that Sara's transaction has reached the mempool:

```
bitcoin-cli -regtest getmempoolinfo
bitcoin-cli -regtest getrawtransaction "$TXID" true
```

The transaction must be available to the mining node. If Sara and Omar are on separate VMs, their nodes must be connected and synchronized.

Mine one block on Omar's node:

```
OMAR_ADDRESS=$(bitcoin-cli -regtest -rpcwallet=omar getnewaddress)

bitcoin-cli -regtest generatetoaddress 1 "$OMAR_ADDRESS"
```

Then, once Sara's node has received and processed the block, run:

```
bitcoin-cli -regtest -rpcwallet=sara listunspent
bitcoin-cli -regtest getrawtransaction "$TXID" true
```

The new transaction should have at least one confirmation if it was included in the mined block.

## 5. Experiment D — Compare the lifecycle

Record your observations in this table as you execute the commands.

| Stage                   | What to inspect                     | Expected observation                            |
| ----------------------- | ----------------------------------- | ----------------------------------------------- |
| Created                 | `getrawtransaction`                 | New `vout` entries exist                        |
| Available               | `listunspent 0`                     | Wallet recognizes the output                    |
| Selected                | `vin` of the spending transaction   | Previous `txid` and `vout` are referenced       |
| Spent                   | `gettxout` on the consumed outpoint | Returns `null` if spent                         |
| Removed from UTXO set   | `gettxoutsetinfo` or `gettxout`     | Old output is no longer unspent                 |
| Replaced by new outputs | `vout` of the spending transaction  | Payment and possibly change outputs are created |

Important distinction: the word destroyed in your original diagram is informal. Bitcoin does not erase the old transaction from the blockchain. Its output simply stops being part of the current UTXO set.

## 6. Practice questions

1. Why can a transaction's output appear in the mempool before it has a confirmation?
2. What happens if two transactions attempt to spend the same UTXO?
3. Why does the UTXO set remove an output after it has been spent?
4. If Sara spends a 1 BTC UTXO to pay 0.1 BTC, why might a new UTXO worth approximately 0.9 BTC appear in her wallet?
5. Does spending an output erase the original transaction from the blockchain?

Lab context: your Amine/Sara/Omar Regtest setup and the UTXOs you already captured.&#x20;


Your output shows that Sara's transaction has created two new UTXOs, but they are still unconfirmed. Let's continue Lab 23 step by step.

## 1. Understand your current result

Your transaction ID is:

`5239755c2c4d4b9097ab3cfea8dd78da999cc6378410209be133250d6039bec1`

Output 0 — payment

## 0.10000000 BTC

0 confirmations

Unconfirmed

Output 1 — change

## 0.89999718 BTC

0 confirmations

Unconfirmed

Transaction fee

### 282 sats

The transaction spends an existing UTXO worth 1 BTC and creates two outputs:

\\[ 1.0 = 0.1 + 0.89999718 + 0.00000282 \\]

The fee is 0.00000282 BTC = 282 satoshis.

The two new outputs appear in Sara's `listunspent 0` result because zero-confirmation outputs are included. This indicates the wallet recognizes them as unconfirmed outputs.

## 2. Check whether Omar has the transaction

Run these commands on Omar's machine, not Sara's:

```
bitcoin-cli -regtest getmempoolinfo
```

Then:

```
bitcoin-cli -regtest getrawtransaction \
  5239755c2c4d4b9097ab3cfea8dd78da999cc6378410209be133250d6039bec1 true
```

Interpret the results:

- If the transaction appears in Omar's mempool, he can potentially include it in a block.
- If `getrawtransaction` returns a transaction-not-found error, it may not be in Omar's mempool or accessible through his local transaction index.
- `getmempoolinfo` gives the overall mempool statistics; it does not list every transaction ID.

You can check for this exact transaction using:

```
bitcoin-cli -regtest getmempoolentry \
  5239755c2c4d4b9097ab3cfea8dd78da999cc6378410209be133250d6039bec1
```

## 3. Mine one block on Omar's node

If Omar's node has the transaction in its mempool, run:

```
OMAR_ADDRESS=$(bitcoin-cli -regtest -rpcwallet=omar getnewaddress)

bitcoin-cli -regtest generatetoaddress 1 "$OMAR_ADDRESS"
```

This mines one block. If the transaction is included, it will receive its first confirmation.

Now check Sara's node:

```
bitcoin-cli -regtest getrawtransaction \
  5239755c2c4d4b9097ab3cfea8dd78da999cc6378410209be133250d6039bec1 true
```

And:

```
bitcoin-cli -regtest -rpcwallet=sara listunspent
```

If Sara's node has received the new block and the transaction was included, the two new outputs should show at least one confirmation.

## 4. What you have demonstrated in Lab 23

| Lifecycle stage   | Your evidence                                     |
| ----------------- | ------------------------------------------------- |
| UTXO created      | Outputs `0` and `1` in transaction `5239755c...`  |
| UTXO available    | Both outputs appear with `confirmations: 0`       |
| UTXO selected     | Identify the old input in the transaction's `vin` |
| UTXO spent        | The original input is consumed by the transaction |
| New UTXOs created | 0.1 BTC payment and 0.89999718 BTC change         |

Next action: Run `getmempoolentry` for the transaction on Omar's node. That will tell us whether he can mine it from his current mempool.


----------------------------------------------------------------

For Lab 23 — UTXO Lifecycle, let's create 4 UTXOs worth 2 BTC each in Amine's wallet, confirm the transactions by mining a block, and then inspect the resulting UTXOs.

The plan is to create four separate outputs, each worth 2 BTC, sent to four different addresses controlled by Amine.

## Step 1 — Check Amine's wallet

Run these commands on Amine's node:

```
bitcoin-cli -regtest listwallets
bitcoin-cli -regtest -rpcwallet=amine getbalance
bitcoin-cli -regtest getblockchaininfo
```

Ensure the `amine` wallet is loaded and has at least 8 BTC available, plus enough for transaction fees.

## Step 2 — Create four UTXOs of 2 BTC each

Run this Bash script on Amine's node. It generates four addresses and creates four separate transactions, each paying 2 BTC to a different address in Amine's wallet.

```
#!/bin/bash
set -e

WALLET="amine"

for i in 1 2 3 4; do
    ADDRESS=$(bitcoin-cli -regtest -rpcwallet="$WALLET" getnewaddress "utxo-$i")

    TXID=$(bitcoin-cli -regtest -rpcwallet="$WALLET" \
        sendtoaddress "$ADDRESS" 2)

    echo "UTXO $i"
    echo "Address: $ADDRESS"
    echo "Transaction ID: $TXID"
    echo
done
```

Save it as `create_utxos.sh`, then execute:

```
chmod +x create_utxos.sh
./create_utxos.sh
```

This creates four transactions. Their outputs will initially be unconfirmed.

## Step 3 — Inspect the unconfirmed UTXOs

```
bitcoin-cli -regtest -rpcwallet=amine listunspent 0
```

Look for the four outputs of `2.00000000 BTC` with zero confirmations.

The wallet may also show other UTXOs that existed before the experiment.

## Step 4 — Mine a block to confirm them

Generate a mining address from Amine's wallet:

```
MINER_ADDRESS=$(bitcoin-cli -regtest -rpcwallet=amine getnewaddress)

bitcoin-cli -regtest generatetoaddress 1 "$MINER_ADDRESS"
```

Because the four transactions were submitted to the same node, they should normally be available in its mempool for inclusion in the block, provided they remain valid and the block template includes them.

## Step 5 — Verify the four confirmed UTXOs

```
bitcoin-cli -regtest -rpcwallet=amine listunspent
```

You should find the four new 2 BTC outputs with positive confirmation counts, assuming all four transactions were included in the mined block.

Expected result: 4 new UTXOs × 2 BTC = 8 BTC in output value, excluding transaction fees and any other wallet activity.

One subtle point: because each `sendtoaddress` transaction spends an existing UTXO, the four new outputs are created by spending previous outputs. The original inputs are consumed, and change outputs may also be created.

------------------------------------------------------------
The problem is that Omar's fee filter appears to be much higher than Sara's transaction fee rate, so Omar may not be receiving an announcement for Sara's transaction.

Let's understand it using your actual Bitcoin regtest data.

## 1. Compare the two fee values

Sara's transaction fee rate

# 1 sat/vB

Calculated from 141 satoshis ÷ 141 vB

Peer fee filter shown in your logs

# ≈ 9,936 sat/vB

Converted from 0.09936506 BTC/kvB

The apparent difference is enormous: the peer's fee filter is about 9,936 times Sara's transaction fee rate.

## 2. What does a fee filter do?

When Sara wants to relay a transaction to Omar, Bitcoin Core can use the peer's advertised fee filter to decide whether to announce that transaction.

- If the transaction's fee rate is below Omar's filter, Sara may avoid announcing it to Omar.
- If the transaction's fee rate meets the filter, Sara can announce it, subject to other relay rules.
- Even if Sara announces it, Omar independently validates the transaction before accepting it into his mempool.

Important: The fee filter is not the same as Omar's minimum mempool fee. Your Omar output showed `mempoolminfee: 0.00000100 BTC/kvB`, equivalent to 0.1 sat/vB. The high `minfeefilter` value is unusual and should be investigated; it does not by itself establish the definitive cause.

## 3. What should you do next?

Run on Sara:

```
bitcoin-cli -regtest getmempoolinfo
bitcoin-cli -regtest getpeerinfo
```

Run on Omar:

```
bitcoin-cli -regtest getmempoolinfo
bitcoin-cli -regtest getpeerinfo
```

Compare the current `minfeefilter` values for the specific connection between Sara and Omar.

Also check the actual transaction fee rate using:

```
bitcoin-cli -regtest getmempoolentry "5239755c2c4d4b9097ab3cfea8dd78da999cc6378410209be133250d6039bec1"
```

For your experiment, the key distinction is between transaction relay being filtered by the sender and the receiving node rejecting a transaction. Those are different failure modes, and the logs should help you distinguish them.

------------------------------------------------------------
# Lab 23 — UTXO Lifecycle: Summary

## 1. What is a UTXO?

A UTXO (Unspent Transaction Output) is an output from a Bitcoin transaction that has not yet been spent.

Bitcoin tracks spendable outputs rather than storing your balance as a single account number.

Each UTXO is identified by:

- `txid`: ID of the transaction that created it.
- `vout`: index of the output within that transaction.
- `amount`: value in BTC.
- `scriptPubKey`: conditions required to spend it.

## 2. The complete UTXO lifecycle

1\. UTXO created

A transaction creates an output in `vout`.

2\. UTXO available

The output is unspent and can potentially be selected by a wallet.

3\. UTXO selected

The wallet selects the output as an input for a new transaction.

4\. UTXO spent

The new transaction references the old output in `vin`.

5\. Removed from the UTXO set

The old output is no longer available to spend.

6\. New UTXOs created

The transaction creates new outputs for the recipient and possibly the sender's change.

Important: Spending a UTXO does not erase the historical transaction from the blockchain. It removes that output from the current UTXO set.

## 3. Your Regtest experiment

You created a transaction with ID:

`5239755c2c4d4b9097ab3cfea8dd78da999cc6378410209be133250d6039bec1`

It produced two outputs:

| Output    | Amount         | Initial status |
| --------- | -------------- | -------------- |
| `vout: 0` | 0.10000000 BTC | Unconfirmed    |
| `vout: 1` | 0.89999718 BTC | Unconfirmed    |

The transaction spent a previous UTXO worth 1 BTC.

\\[ 1 = 0.1 + 0.89999718 + 0.00000282 \\]

The fee was 282 satoshis.

You then investigated why the transaction appeared in Sara's mempool but not Omar's. Your peer information showed active P2P connections, demonstrating that having connected nodes does not guarantee that every transaction will propagate.

## 4. Commands to remember

| Command                                               | Purpose                                    |
| ----------------------------------------------------- | ------------------------------------------ |
| `bitcoin-cli -regtest -rpcwallet=amine listunspent`   | List confirmed wallet UTXOs                |
| `bitcoin-cli -regtest -rpcwallet=amine listunspent 0` | Include unconfirmed outputs                |
| `bitcoin-cli -regtest getrawtransaction TXID true`    | Inspect a transaction's inputs and outputs |
| `bitcoin-cli -regtest gettxout TXID VOUT`             | Check whether an output remains unspent    |
| `bitcoin-cli -regtest getrawmempool`                  | List transaction IDs in the local mempool  |
| `bitcoin-cli -regtest getpeerinfo`                    | Inspect P2P connections                    |
| `bitcoin-cli -regtest generatetoaddress 1 ADDRESS`    | Mine one regtest block                     |

## 5. Five concepts to remember

1. `vin` consumes old outputs.
2. `vout` creates new outputs.
3. A UTXO is identified by its `txid` and output index.
4. A transaction in the mempool is unconfirmed; it is not yet part of a block.
5. When a transaction is confirmed, its inputs are spent and its outputs become part of the confirmed UTXO set, provided those outputs remain unspent.

The main objective of Lab 23 is to understand how Bitcoin continuously replaces spent outputs with new outputs while maintaining a valid, spendable UTXO set.