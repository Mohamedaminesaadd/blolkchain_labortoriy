# Bitcoin Data Directory Investigation

Bitcoin Data Directory Investigation means understanding where Bitcoin Core stores its blockchain, wallets, configuration, logs, and other node data on your computer.

In your lab, you installed Bitcoin Core under `/opt/bitcoin`. But there is an important distinction:

- `/opt/bitcoin/` contains the Bitcoin Core software and your custom configuration file.
- `~/.bitcoin/` normally contains the node's data, including the regtest blockchain and wallet data.

Because you're using `-conf=/opt/bitcoin/bitcoin.conf`, your configuration file is stored in `/opt/bitcoin/`, but the data directory normally remains `~/.bitcoin/` unless you configure `datadir` differently.

## 1. Understand the directory structure

## Your Bitcoin Core installation

`/opt/bitcoin/`

Software installation and your custom configuration

`bin/bitcoin-cli` — RPC client

`bin/bitcoind` — Bitcoin node

`bin/bitcoin-qt` — graphical interface

`bitcoin.conf` — your configuration

`~/.bitcoin/`

Default data directory for the current Linux user

`blocks/` — block data files

`chainstate/` — current chain validation state

`regtest/` — regtest-specific data

`wallets/` — wallet files, if stored here

`debug.log` — node log in the data directory

The exact contents vary with Bitcoin Core version, network, configuration, and wallet setup.

## 2. Step 1 — Find your actual data directory

On your Amine host, run:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getdatadir
```

If that RPC method is unavailable in your Bitcoin Core version, inspect the running process and configuration instead.

You can also inspect the default location:

```
ls -la ~/.bitcoin/
```

To inspect the regtest directory:

```
ls -lah ~/.bitcoin/regtest/
```

And to inspect the configuration:

```
cat /opt/bitcoin/bitcoin.conf
```

These commands only inspect your setup; they do not modify or delete data.

## 3. Step 2 — Understand the important files

| Directory or file | Purpose                                                                   |
| ----------------- | ------------------------------------------------------------------------- |
| `blocks/`         | Stores downloaded or generated block data, typically in `blk*.dat` files. |
| `chainstate/`     | Stores the current validated UTXO set and related chainstate data.        |
| `blocks/index/`   | Stores block-index database data.                                         |
| `wallets/`        | Stores wallet databases when using the default wallet location.           |
| `debug.log`       | Records node events, errors, and diagnostic information.                  |
| `mempool.dat`     | May store a saved mempool across restarts when enabled and available.     |
| `peers.dat`       | Stores information about known network peers.                             |

Important: the blockchain files and wallet files serve different purposes. The block files hold blockchain data; wallet data manages keys and wallet-related transaction information. The wallet is not the blockchain itself.

## 4. Step 3 — Investigate your regtest blockchain

You mined Block 103 in your lab. Let's connect the RPC view to the files on disk.

First, check the current height:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockcount
```

Then inspect the regtest data directory:

```
du -sh ~/.bitcoin/regtest/blocks
du -sh ~/.bitcoin/regtest/chainstate
```

`du -sh` reports the disk space occupied by each directory.

You can inspect the block files:

```
ls -lh ~/.bitcoin/regtest/blocks/
```

The files named `blk*.dat` contain serialized block data. They are not plain-text files, so opening them with `cat` will not display a readable list of transactions. Use Bitcoin Core RPC to inspect their contents.

For example:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockhash 103
```

Then use the resulting hash:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblock <HASH> 2
```

## 5. Step 4 — Why this matters for your four nodes

Your Amine host, Master VM, Omar VM, and Sara VM each have their own data directory.

That means:

- Each node stores its own copy of blockchain data.
- Each node maintains its own chainstate and mempool.
- Wallets belong to the node's wallet storage and configuration.
- Restarting a node normally preserves its data.
- Deleting a data directory can destroy local wallet data or require the blockchain to be reconstructed.

Do not assume that deleting `/opt/bitcoin/` and deleting `~/.bitcoin/` have the same effect. One is your software installation; the other normally holds your node's persistent data.

## 6. Your practical investigation checklist



-------------------------------------------------------------------
Excellent. You have found your Bitcoin Core data directory: `~/.bitcoin`. This is where Bitcoin Core stores blockchain data, its current transaction state, wallet files, peer information, and logs.

Since you're using Bitcoin Core 31.1 and building a regtest lab, let's investigate what each file does and how the pieces work together.

# 1. Understand your Bitcoin data directory

`blocks/` — Historical blockchain data

Block storage

Stores serialized block data, including block headers, transactions, and other block information. Files commonly have names such as `blk00000.dat`.

Your node uses these blocks to validate the blockchain and reconstruct historical information.

`chainstate/` — Current UTXO database

Current spendable outputs

Stores the current set of unspent transaction outputs (UTXOs), using a LevelDB database.

When Amine sends BTC to Sara, Bitcoin Core checks whether the transaction spends valid, unspent outputs.

`wallets/` — Wallet data

Stores wallet databases, which can contain keys, addresses, transaction records, and wallet metadata.

Your miner, Sara, and Amine wallets may be stored here if you created them with this node's wallet directory.

`regtest/` — Regtest-specific blockchain state

This directory holds the regtest network's own blockchain data and related files. Since you use `-regtest`, this is the first directory to investigate for your lab.

`debug.log` — Node activity log

Records diagnostic messages about startup, peers, block validation, and other node activity. Useful when debugging your Bitcoin network.

## 2. What are the other files?

| File                | Purpose                                                                               |
| ------------------- | ------------------------------------------------------------------------------------- |
| `anchors.dat`       | Stores peer addresses used as connection anchors to help reconnect to peers.          |
| `banlist.json`      | Stores peers that have been banned.                                                   |
| `fee_estimates.dat` | Persists transaction-fee estimates when available.                                    |
| `.lock`             | Helps prevent multiple processes from opening the same data directory simultaneously. |
| `mempool.dat`       | Can preserve pending transactions across restarts.                                    |
| `peers.dat`         | Stores information about known peers.                                                 |
| `settings.json`     | Stores runtime settings managed by Bitcoin Core.                                      |

These files are maintained by Bitcoin Core. Avoid manually editing or deleting them while the node is running.

# 3. Investigate the actual regtest directory

Your listing shows that `regtest/` was modified on October 10, while the top-level `blocks/` and `chainstate/` were last modified on October 8. That is a useful clue that different network-specific data may be involved.

Run these commands:

Lab 01 — Inspect regtest contents

```
ls -lah ~/.bitcoin/regtest
```

Lab 02 — Find the block files

```
find ~/.bitcoin/regtest -maxdepth 3 -type f
```

Lab 03 — Check the active blockchain

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf \
  -regtest getblockchaininfo
```

Lab 04 — Check your wallet list

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf \
  -regtest listwallets
```

These commands are read-only and will help us understand your actual setup.

# 4. How the data works together when Amine sends 2 BTC to Sara

Amine's wallet

Selects available UTXOs and creates a signed transaction.

Mempool

The node checks the transaction before block confirmation.

Block storage: `blocks/`

A miner includes the transaction in a block.

UTXO database: `chainstate/`

The spent outputs are removed and the new outputs are added to the current UTXO set.

This diagram is conceptual. The actual data directory layout depends on the network and configuration, and the wallet's view of transactions is separate from the consensus UTXO database.

For example, if Amine spends a 5 BTC UTXO to send Sara 2 BTC, the transaction might create:

- 2 BTC for Sara.
- Approximately 3 BTC as change back to Amine, minus the transaction fee.

Bitcoin does not modify the original 5 BTC output. It marks that output as spent in the resulting ledger state and creates new outputs.

# 5. Your next challenge

Let's determine exactly where your regtest blocks are stored before inspecting individual block files.

Run:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf \
  -regtest getblockcount
```

Then:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf \
  -regtest getblockhash 100
```

And finally:

```
ls -lah ~/.bitcoin/regtest/blocks
```



You're very close, but there is one critical distinction: deleting `~/.bitcoin/` can destroy your local wallet keys and blockchain data, but it does not automatically destroy Bitcoin that exists on the network.

Let's break it down using your lab.

## 1. What is stored in `~/.bitcoin/`?

With your default data directory, the structure is approximately:

`~/.bitcoin/`

Bitcoin Core's default data directory

`wallets/` — Wallet data

Contains wallet databases, which may hold private keys, descriptors, addresses, and transaction information.

`regtest/blocks/` — Block data

Stores the blocks your node has downloaded or mined.

`regtest/chainstate/` — UTXO set

Stores the node's current view of unspent transaction outputs, not your wallet's private keys.

`regtest/debug.log` — Logs

Contains diagnostic messages about node operation.

The exact paths depend on your configuration. Your `bitcoin.conf` is at `/opt/bitcoin/bitcoin.conf`, but your data directory is normally `~/.bitcoin/` unless overridden.

## 2. What happens if you delete `~/.bitcoin/`?

| Item                                           | Likely consequence                                                      |
| ---------------------------------------------- | ----------------------------------------------------------------------- |
| Private keys stored only in the deleted wallet | You can lose the ability to spend the funds controlled by those keys.   |
| Local wallet database                          | Lost unless you have a backup or another recoverable copy.              |
| Downloaded/mined blockchain data               | Lost locally; it may be downloaded or reconstructed again if available. |
| Local UTXO set (`chainstate`)                  | Lost locally; Bitcoin Core can rebuild it by validating the chain.      |
| Bitcoin recorded on a shared blockchain        | Not deleted by removing your local files.                               |

### Example from your lab

Suppose Sara has a confirmed UTXO worth `0.99999859 BTC`.

```
Bitcoin blockchain
       │
       └── Records an unspent output of 0.99999859 BTC
                          │
                          ▼
                 Sara's private key
                 authorizes spending
```

If Sara's wallet database is deleted:

- The output remains recorded in the blockchain.
- The blockchain does not know that Sara deleted a file.
- If Sara loses the only private key that can spend the output, she may permanently lose access to those funds.
- If she has a valid wallet backup, she may be able to recover the key and spend them.

Important: your current lab uses `regtest`, a private testing chain. Its BTC are test coins, not real Bitcoin mainnet funds.

## 3. The difference between wallet keys and UTXOs

This is fundamental to understanding Bitcoin.

- Private key: gives you the cryptographic ability to authorize certain spends.
- UTXO: an unspent output recorded in the blockchain state.
- Wallet: manages keys and helps identify and spend outputs belonging to it.
- Blockchain: records transactions and the history from which the current UTXO set is derived.

Your wallet does not contain the BTC themselves. The BTC are represented by outputs in the blockchain; the wallet holds the cryptographic material needed to spend outputs it controls.

## 4. Safely inspect your wallet files

On a node, run:

```
ls -lah ~/.bitcoin/
```

Then:

```
ls -lah ~/.bitcoin/regtest/
```

And:

```
ls -lah ~/.bitcoin/regtest/wallets/
```

The last directory may not exist if your wallet is stored elsewhere or the wallet uses a different configuration.

Never delete these directories just to troubleshoot Bitcoin Core. First identify the data directory and back up your wallets safely. A wallet backup should be made using an appropriate Bitcoin Core wallet-backup procedure, and you should protect it because it can contain spendable private keys.

## Practice questions

1. If Sara deletes her wallet but the blockchain remains intact, what information is lost?
2. Why can Bitcoin Core rebuild `chainstate` but cannot automatically recreate a lost private key?
3. What is the difference between a wallet backup and a blockchain backup?
4. If Sara has a valid wallet backup, can she recover access to her UTXOs after reinstalling Bitcoin Core?

-------------------------------------------------------------------
Yes! If you copy the complete Bitcoin data directory from PC A to PC B, you can generally recover the wallets, wallet keys, blockchain data, and UTXO state on PC B. There are a few important conditions.

Let's use your example: PC A contains Bitcoin Core, and you want PC B to continue using the same node data.

## 1. What transfers from PC A to PC B?

PC A — Old computer

Bitcoin data directory

Stop Bitcoin Core, then copy the complete directory

Transfer the data directory

Wallet files · Blocks · Chainstate · Configuration, if included

PC B — New computer

Bitcoin Core opens the copied data

| Data                                    | What happens on PC B?                                                                                  |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Wallet files and private keys           | Recoverable if the complete, valid wallet data was copied.                                             |
| Wallet balances and transaction history | Usually recoverable from the wallet and blockchain data, with synchronization or rescanning if needed. |
| `blocks/`                               | Provides the copied block data.                                                                        |
| `chainstate/`                           | Provides the copied UTXO state, subject to compatibility and validation.                               |
| `debug.log`                             | Copies diagnostic history, but is not needed to recover the wallet.                                    |
| Peer information                        | May be copied, but PC B will establish its own network connections.                                    |

## 2. The most important condition: copy the correct directory

In your setup, you use:

```
/opt/bitcoin/bitcoin.conf
```

But your node's data is normally stored separately:

```
~/.bitcoin/
```

unless you set `datadir` in the configuration or pass `-datadir` on the command line.

On PC A, identify the actual data directory:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
```

Then inspect the configuration and default directory:

```
cat /opt/bitcoin/bitcoin.conf
ls -lah ~/.bitcoin/
```

Make sure you copy the directory that actually contains the wallet and blockchain data, not just the Bitcoin Core software under `/opt/bitcoin/`.

## 3. How to transfer it safely

1. Stop Bitcoin Core on PC A so wallet and database files are not being modified during the copy.
   ```
   bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf stop
   ```
2. Confirm the process has stopped before copying the data.
3. Copy the complete data directory to PC B, preserving file permissions and ownership.
4. Install a compatible Bitcoin Core version on PC B and configure it to use the copied data directory.
5. Start Bitcoin Core on PC B and inspect the blockchain and wallet.

For example, after the copy, if PC B uses the default directory:

```
bitcoin-cli getblockchaininfo
bitcoin-cli -rpcwallet=sara getbalances
```

The wallet command assumes the `sara` wallet exists in the copied wallet data and is loaded. If it isn't loaded, you may need to load it first.

Important: don't run two Bitcoin Core processes against the same data directory simultaneously. Also, keep a separate wallet backup before migration. The configuration file, RPC credentials, and data directory may be stored in different places, so copying one does not necessarily transfer all of them.

## 4. What if PC B has the wallet but not the blockchain?

That can still work.

- If you copy the wallet files and keys, you can potentially recover the wallet on PC B.
- If you also copy the blockchain data, PC B can reuse those local blocks, provided the data is compatible.
- If the blockchain data is missing, Bitcoin Core can download or rebuild the chain state, and the wallet may need to rescan the blockchain to discover its transactions.

The key distinction is that private keys let you spend your funds; blockchain data lets your node verify the transactions and determine which outputs remain unspent.

One final caveat: if PC A uses `regtest`, PC B must use the same regtest chain to continue that lab. Copying mainnet data and opening it as regtest will not work as a continuation of the same chain.

## Practice questions

1. If you copy only `wallets/` to PC B, what information might still be missing?
2. Why should Bitcoin Core be stopped before copying its database files?
3. Can PC B recover the wallet keys if the blockchain files are missing?
4. Why must PC B use the same network, such as `regtest` or `mainnet`, to continue the same chain?
5. If both PCs use the same wallet backup, can they independently create conflicting spends of the same UTXO? What would happen when those transactions reach the network?
