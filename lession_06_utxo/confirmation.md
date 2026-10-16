# What is a confirmation in Bitcoin?

A confirmation means that a Bitcoin transaction has been included in a block that belongs to the active blockchain.

When you send 2 BTC to Sara, the transaction is not confirmed just because you broadcast it. A miner must include it in a valid block, and Bitcoin nodes must accept that block into the active chain.

## 1. How confirmations work

```
Amine sends 2 BTC to Sara
          |
          v
Transaction enters a node's mempool
          |
          v
Miner includes it in a block
          |
          v
Block accepted into active blockchain
          |
          v
      1 confirmation
          |
          v
Another block is added
          |
          v
      2 confirmations
          |
          v
More blocks are added
          |
          v
      3, 4, 5... confirmations
```

## 2. What do 1, 2, and 6 confirmations mean?

## 0

Unconfirmed

The transaction has not been included in a block in the active chain. It may be in a mempool.

## 1

One confirmation

The transaction is included in a block in the active chain.

## 2

Two confirmations

One additional block has been added after the transaction's block.

## 6

Six confirmations

The transaction's block has five additional blocks built on top of it. This provides stronger confidence against a chain reorganization.

More confirmations generally make it increasingly difficult to replace the transaction through a competing chain. Six confirmations is a common rule of thumb for higher-value payments, not an absolute guarantee or a universal requirement.

## 3. Why are confirmations important?

Confirmations help protect against double spending.

Suppose Amine broadcasts two conflicting transactions that spend the same UTXO:

```
Original UTXO: 3 BTC
        |
        +---- Transaction A → Sara
        |
        +---- Transaction B → Omar
```

If Transaction A is included in a valid block that remains in the active chain, Transaction B cannot spend the same original UTXO in that chain history.

As more blocks are added, reversing that history generally becomes more difficult.

## 4. How to check confirmations in your Bitcoin Core lab

For Omar's wallet:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions "*" 10
```

Find the transaction and look for:

```
{
  "txid": "example_transaction_id",
  "confirmations": 3
}
```

The example shows three confirmations.

You can also inspect a specific wallet transaction:

```
bitcoin-cli -regtest -rpcwallet=omar gettransaction "TXID"
```

Look for the `confirmations` field.

Because you're using `regtest`, you can generate blocks manually to increase confirmations:

```
bitcoin-cli -regtest -rpcwallet=omar getnewaddress
```

Copy the returned address, then:

```
bitcoin-cli -regtest generatetoaddress 1 "OMAR_ADDRESS"
```

If a transaction was already confirmed, mining another block on top of its block will generally increase its confirmation count by one, provided the active chain remains unchanged.

Remember: A transaction can be valid but unconfirmed. Confirmation means it has been included in a block in the active chain.

## Questions to explore next

1. Why does each new block increase a transaction's confirmation count?
2. What is a blockchain reorganization, and how can a transaction lose confirmations?
3. Why does a coinbase transaction need 100 confirmations before its reward can be spent?
4. Is a transaction with one confirmation guaranteed to be permanent?

Yes, exactly! If you send 1 BTC to Omar, he may need to wait for a confirmation before spending it, but it does not necessarily take 10 minutes.

The key distinction is between the transaction being received and the transaction being confirmed.

## 1. What happens when you send 1 BTC to Omar?

Step 1 — You send 1 BTC

Your wallet broadcasts the transaction to the Bitcoin network. It can reach Omar's node within seconds, depending on network conditions.

Step 2 — Omar receives the transaction

The transaction may appear in Omar's wallet as unconfirmed. It is in the mempool, but it has not yet been included in a block.

Step 3 — A miner confirms it

A miner includes the transaction in a block. Omar's transaction now has 1 confirmation.

Step 4 — Omar spends the 1 BTC

Once the output is available and spendable in his wallet, Omar can generally create a transaction spending it after just 1 confirmation. He does not need to wait for six confirmations in ordinary Bitcoin Core wallet operation.

## 2. Does he have to wait 10 minutes?

No. On Bitcoin mainnet, blocks are produced on average every 10 minutes, but this is not a fixed timer.

- A block might arrive in 30 seconds.
- Another might take 20 minutes or longer.
- Omar might see the transaction before a block confirms it.

Waiting for one confirmation is common, but some recipients wait for more confirmations before accepting a payment as sufficiently secure. The appropriate number depends on the amount and the risk of a conflicting transaction.

Important exception: newly mined coinbase rewards have a special maturity requirement of 100 confirmations before they can be spent. That does not apply to an ordinary 1 BTC payment from your wallet to Omar.

## 3. Try it in your Bitcoin regtest lab

In your lab, blocks are not automatically mined every 10 minutes. You control mining, so you can confirm a transaction almost immediately by generating a block.

```
# 1. Send 1 BTC from your wallet to Omar
bitcoin-cli -regtest -rpcwallet=YOUR_WALLET sendtoaddress "OMAR_ADDRESS" 1

# 2. Check the transaction's confirmation count
bitcoin-cli -regtest -rpcwallet=YOUR_WALLET listtransactions "*" 10
```

Then mine a block to confirm the transaction:

```
# Get a mining address from a loaded wallet
bitcoin-cli -regtest -rpcwallet=omar getnewaddress

# Mine one block to that address
bitcoin-cli -regtest generatetoaddress 1 "MINING_ADDRESS"
```

Replace `YOUR_WALLET`, `OMAR_ADDRESS`, and `MINING_ADDRESS` with your actual values. If Omar's wallet is on another VM, ensure the transaction reaches the node holding that wallet.

Questions you can ask next:

1. Can Omar spend an unconfirmed Bitcoin transaction?
2. What happens if I send the same BTC to two different people?
3. How can I see the transaction change from 0 to 1 confirmation in my lab?



Yes! Omar can sometimes spend an unconfirmed Bitcoin payment, even with 0 confirmations. If he trusts you, he may choose to accept it, but trust does not change how Bitcoin validates transactions.

## 1. How does it work with 0 confirmations?

Imagine you send 1 BTC to Omar.

You send 1 BTC to Omar

Your wallet broadcasts the transaction.

0 confirmations

Omar's node sees the transaction in its mempool, but it has not been included in a block.

Omar accepts

He may create another transaction spending the received output if his wallet and node allow it.

Risk

The original payment might never confirm, or a conflicting transaction might confirm instead.

## 2. If Omar knows you, can he trust the payment?

He can decide to accept the risk, especially for a small payment between friends. But there are two different kinds of trust:

- Trust in you: Omar believes you will not intentionally deceive him.
- Trust in the transaction: Omar knows the payment has been accepted into a valid block and is becoming harder to reverse.

Even if you are honest, the transaction might be delayed because of a low fee, or it might conflict with another transaction spending the same inputs.

For example, you broadcast a payment of 1 BTC to Omar, then broadcast a conflicting transaction spending the same input to another address. If the network accepts the conflicting transaction into the active blockchain, Omar's original payment will not be confirmed in that chain.

## 3. Can Omar spend the unconfirmed output?

Often, yes. This is called unconfirmed transaction chaining.

Example:

```
Transaction A: You ── 1 BTC ──> Omar
                         0 confirmations

Transaction B: Omar ── 0.4 BTC ──> Sara
                         0 confirmations
```

Transaction B spends an output created by Transaction A. Both transactions can remain unconfirmed in the mempool, and miners can include them in the blockchain in dependency order.

However, wallet behavior and node policy can restrict this. If Transaction A is replaced, rejected, or never confirmed, Transaction B may also fail to confirm.

## 4. Test it in your regtest lab

You can demonstrate this without waiting for real Bitcoin blocks. Regtest lets you control when blocks are mined.

First, send a payment:

```
bitcoin-cli -regtest -rpcwallet=YOUR_WALLET \
  sendtoaddress "OMAR_ADDRESS" 1
```

Before mining a block, check the transaction:

```
bitcoin-cli -regtest getmempoolinfo
bitcoin-cli -regtest getrawmempool
```

Then inspect Omar's wallet transactions:

```
bitcoin-cli -regtest -rpcwallet=omar listtransactions "*" 10
```

The payment may appear with `"confirmations": 0` if the transaction has reached Omar's node and is recognized by his wallet. If Omar spends it before confirmation, you can observe how the dependent transaction behaves when you mine a block.

Important: Bitcoin mainnet and regtest have different mining conditions and policies. A test that succeeds on regtest does not prove that every unconfirmed transaction will be accepted on mainnet.

### Questions you can ask next

1. How does a double-spend attack work step by step?
2. How can I make Omar spend an unconfirmed output in my regtest lab?
3. What is Replace-By-Fee (RBF), and how can it affect an unconfirmed payment?



Yes! A Bitcoin transaction can remain unconfirmed for a long time and eventually be dropped from a node's mempool. But waiting for many blocks does not automatically invalidate a transaction.

Let's distinguish three cases.

## 1. Three possible situations

Case A — Transaction remains unconfirmed

You send 1 BTC to Omar. The transaction stays in the mempool and has 0 confirmations. It might remain unconfirmed for minutes, hours, or longer.

Case B — Transaction is dropped from the mempool

A node may remove a transaction because of mempool expiry, memory limits, or other policy reasons. The transaction can disappear from that node's mempool, but this does not mean it is permanently invalid. It might be rebroadcast later.

Case C — A conflicting transaction is confirmed

If you spend the same Bitcoin inputs in another transaction and that conflicting transaction gets confirmed first, the original transaction becomes invalid for the active blockchain because its inputs have already been spent.

## 2. What if Omar waits for 100 blocks?

Imagine this sequence:

```
Block 1000: You broadcast 1 BTC to Omar
             Confirmations = 0

Blocks 1001–1100: The transaction stays unconfirmed
                  Confirmations = 0

Block 1101: Another transaction spends the same inputs
            and gets confirmed

Result: Your original transaction cannot be confirmed
        using those same inputs on this chain.
```

The exact block count is illustrative. The important point is that the competing transaction spending the same inputs, not the number of blocks that passed, prevents the original from being confirmed.

If the original transaction is merely dropped from the mempool and its inputs remain unspent, it may still be valid later.

## 3. How does this affect Omar?

If Omar accepts your payment at 0 confirmations and immediately spends it, he is taking a risk. If your original payment later conflicts with another transaction, Omar's dependent transaction may also fail to confirm.

For a real payment, waiting for confirmations reduces this risk. Each additional confirmation makes reversal increasingly difficult, although it never creates an absolute mathematical guarantee of permanence.

## 4. Try checking your regtest mempool

```
# Show transactions currently in the mempool
bitcoin-cli -regtest getrawmempool

# Show mempool statistics
bitcoin-cli -regtest getmempoolinfo

# Check whether a specific output is still unspent
bitcoin-cli -regtest gettxout "TXID" VOUT
```

Replace `TXID` and `VOUT` with the transaction ID and output index. If `gettxout` returns `null`, that output is not currently available as an unspent output under the query's chain/mempool view.

### Questions you can ask next

1. How does Bitcoin know that two transactions spend the same input?
2. Can I simulate a double-spend conflict between Amine and Omar in regtest?
3. What is the difference between a transaction being dropped and being invalid?