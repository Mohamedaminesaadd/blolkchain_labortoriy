# Bitcoin Network Types — Beginner to Advanced

Bitcoin Core has several network types. Each one determines which blockchain your node uses, which peers it can communicate with, and whether the coins are real or for testing.

For your lab with Amine, Master, Omar, and Sara, understanding these networks is essential because you've been using `regtest` to mine blocks and send test BTC.

## 1. The four network types to know

[Bitcoin  in bright orange color on black background. Vector.](https://images.openai.com/static-rsc-4/XsWb9H0UCDc7-FGYPrRKyFudo_ldUmT54k35ovGXSqNqwudcN4ix2OXmOfRuJVZd9lUis8HvaQNxnDlh_aq4s97cCi4Xt1wWkRZrkXdQ3VTtubwxY2YfhAxPW0D_pjlfjpYbr81EgQdtZkR1bw25l_DTle6nguYh2WZHluQ9z6O7KKFCza9r3dYacdoNmAXz?purpose=inline)

1\. Mainnet — the real Bitcoin network

Real BTC

The production network used for real Bitcoin transactions. Nodes connect to mainnet peers and validate the mainnet blockchain.

Typical P2P port: `8333` · RPC port: `8332`

[Start9 Marketplace](https://images.openai.com/static-rsc-4/F_Dk48d1QgdBC-T9zZvzoKEFIxxPBmgUhwzpVK-1PABseiLAI3sNNRWoHTB9rx8IytjE_YOXaXwiTCz2LsDx5voUApdxy3Q_xyrg18JlfekyNkXSmB1qaRP0BD3rt3Y7SLvtkPiamUoSVJxf90m4uzLclUlLufUjn8S21tJbwBE?purpose=inline)

2\. Testnet — public testing network

Developers can test software on a shared network without using mainnet BTC. Testnet coins are not intended to have mainnet Bitcoin's value.

Traditional Testnet3 ports: P2P `18333` · RPC `18332`

[Consensus Cleanup: demo of slow blocks on Signet - Protocol Design - Delving Bitcoin](https://images.openai.com/static-rsc-4/zVX5WeqI4NqNF5uxQCw5HvS2blpIwQU0PmRxbgQJK42Iv-zOtqIXqLuda2k5E2nJVrjYAN_6oMRo91ZV5DH5JxmlWgx6saTkT4XqGey42chfiyXfycB_MpZvlPP3kyJsQSvVP4cVyBwqowEUx4Wf1TIU7Y8-YX1fxxiONoerHxQ?purpose=inline)

3\. Signet — controlled public testing network

A shared test network where block production is governed by a signature-based challenge. It offers more controlled block production than ordinary proof-of-work test networks.

Default Signet ports: P2P `38333` · RPC `38332`

[Indicate network in the Node window title - similar to the main window · Issue #544 · bitcoin-core/gui · GitHub](https://images.openai.com/static-rsc-4/hF11dvEjfGn0F_PpGjvpQeFY5mRlDY7YxLgU3igtfkM1AYruVsyHgZZ4RKWNK1kmReObMflK9WrOzMWOBoTTtfGwe6Lah067xc_7DJqfIXXyODxJ_Xy6UVxcX5uLOpE0wNUtwdFlqF9nWYXxPkWozJESyBodIjZjAUML_KwN670?purpose=inline)

4\. Regtest — your private local lab

A local regression-testing network where you control block generation. You can mine blocks immediately with RPC commands and test transactions between your own nodes.

You're using this now

Default ports: P2P `18444` · RPC `18443`

Port numbers above are Bitcoin Core defaults for these networks; configuration can change them.

## 2. Compare the networks

| Feature                      | Mainnet       | Testnet        | Signet                    | Regtest                    |
| ---------------------------- | ------------- | -------------- | ------------------------- | -------------------------- |
| Real mainnet BTC             | Yes           | No             | No                        | No                         |
| Shared public network        | Yes           | Yes            | Yes                       | Usually private            |
| You control block production | No            | No             | Not normally              | Yes                        |
| Easy, on-demand mining       | No            | No             | No                        | Yes                        |
| Best suited for              | Real payments | Public testing | Controlled shared testing | Local development and labs |

Note that Testnet and Signet coins have their own network-specific addresses and histories. Coins from one network cannot simply be spent on another network.

## 3. How Bitcoin Core selects the network

Your configuration includes:

```
regtest=1
```

That tells Bitcoin Core to use the regtest network.

Check the active network:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
```

Your output should include:

```
{
  "chain": "regtest"
}
```

You can also use:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf -getinfo
```

The exact output depends on your Bitcoin Core version.

### Important: separate data directories

Bitcoin Core keeps network-specific data under the data directory. For example, with the default Linux data directory:

```
~/.bitcoin/
├── blocks/             # Mainnet block data
├── chainstate/         # Mainnet chainstate
├── testnet3/           # Traditional Testnet3 data
├── testnet4/           # Testnet4 data, if used
├── signet/             # Signet data
└── regtest/            # Your private lab
```

Not every directory will exist on your computer. The exact structure depends on the networks you've used and your Bitcoin Core version.

Your Block 103 and your Amine/Sara/Omar transactions belong to your regtest chain, not Bitcoin mainnet.

## 4. Try this in your lab

Run this on Amine:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
```

Then compare:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockcount
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getnetworkinfo
```

The first reports chain information, the second gives the current best block height, and the third reports P2P network information.

Do not change `regtest=1` to `mainnet` on your existing lab just to experiment: mainnet uses a different chain and real funds. Keep your regtest setup intact.

## 5. Practice questions

Try answering these without looking back:

1. Why can you mine Block 103 instantly in regtest but not on mainnet?
2. If Amine is using regtest and Sara is using mainnet, can they directly exchange the same transaction over their ordinary Bitcoin P2P connections?
3. What is the difference between Testnet and Signet?
4. If you delete the `regtest/` directory, does that delete your mainnet blockchain?
5. Which network would you choose to test a wallet application with your four VMs, and why?

Next topic: Bitcoin P2P networking — how Amine, Master, Omar, and Sara discover peers, exchange transactions, and synchronize blocks.



----------------------------------------------------------------
### the probleme of the synchronize block 
The problem we solved was a blockchain synchronization problem between Amine's Bitcoin node and the Master node in your regtest lab.

Amine had Block 102, while Master had already reached Block 103. We discovered that Amine had no connected peers, so it could not receive the newer block from Master. We then connected Amine to Master using Bitcoin's P2P network.

Let's examine the problem, its possible causes, its consequences, and the solution.

## 1. The initial problem

Your lab was in this state:

Master

# 103

Latest block height

Amine

# 102

One block behind

The key difference

Master knew Block 103, whose hash was:

`2c10e73d2eeb5b8856c31ca27a5def38b52616c899fad26812a8bd04974cba9d`

Amine returned `Block not found` when asked for that hash and `getpeerinfo` initially returned an empty array.

This did not necessarily mean that Amine's blockchain was corrupted. It meant that the node's current view of the chain was behind Master.

## 2. What caused the problem?

The direct issue we observed was the absence of a P2P connection.

Before the fix, Amine's `getpeerinfo` returned:

```
[]
```

This means Amine had no active Bitcoin P2P peers at that moment.

Without a peer, Amine could not learn about Master’s new blocks through the network.

The underlying reason why Amine had no peers was not conclusively established. Possible explanations include:

- No connection configured: Amine was not connected to Master.
- A restarted node: A manually added peer may need to be added again after a restart, depending on the configuration.
- Different data directories or configurations: If Bitcoin Core starts with a different datadir, it can use a different local blockchain state.
- Network connectivity problems: A firewall, incorrect IP address, or unavailable P2P port could prevent the connection.

We should not claim that a restart or a different datadir definitely caused this incident. We know that the peer was missing; we do not yet know why it was missing.

## 3. What were the consequences?

There were three important consequences.

### A. Amine had an outdated local chain

Master's latest block was 103, but Amine's was 102.

Bitcoin nodes maintain their own local copies of the blockchain. They do not automatically share a single central database.

### B. Amine could not retrieve Block 103 from a peer

The command:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf \
  getblockheader 2c10e73d2eeb5b8856c31ca27a5def38b52616c899fad26812a8bd04974cba9d
```

returned:

```
Block not found
```

That was consistent with Amine not having that block in its local chain data at the time.

### C. Nodes could temporarily disagree about transaction confirmation

Block 103 included three transactions:

- Amine → Master: 2 BTC
- Sara → Omar: 1 BTC
- Amine → Omar: 3 BTC

Until Amine received and accepted Block 103, its local view of these transactions could differ from Master’s. A transaction that Master considers confirmed might still appear unconfirmed to another node that has not received that block.

This is why distributed nodes must synchronize before their views of confirmed transactions agree.

## 4. The solution we applied

We manually connected Amine to Master using the Bitcoin P2P protocol.

On Amine, we ran:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf \
  addnode 192.168.122.100:18444 add
```

Here's what each part means:

| Part                              | Meaning                                              |
| --------------------------------- | ---------------------------------------------------- |
| `bitcoin-cli`                     | Sends an RPC command to the local Bitcoin Core node. |
| `-conf=/opt/bitcoin/bitcoin.conf` | Selects the configuration file.                      |
| `addnode`                         | Requests a connection to a peer.                     |
| `192.168.122.100`                 | Master’s private VM-network IP address.              |
| `18444`                           | Bitcoin's default P2P port for regtest.              |
| `add`                             | Adds a connection to that peer.                      |

We then checked the connection with `getpeerinfo`.

The resulting output contained:

```
{
  "addr": "192.168.122.100:18444",
  "connection_type": "manual",
  "inbound": false,
  "synced_headers": 103,
  "synced_blocks": 103,
  "inflight": []
}
```

These fields tell us:

- `addr`: Amine is connected to Master.
- `connection_type: manual`: The connection was manually requested.
- `inbound: false`: Amine initiated the connection.
- `synced_headers: 103`: Amine's peer synchronization reached header height 103.
- `synced_blocks: 103`: The peer reports synchronization through block height 103.
- `inflight: []`: No blocks were outstanding in that peer's in-flight download list.

The output is strong evidence that the P2P connection worked and Amine caught up. To verify Amine's own local state conclusively, we should also check `getblockchaininfo` and compare `getblockhash 103` with Master.

## 5. What happened technically after the connection?

Step 1 — Peer discovery/connection

Amine established a P2P connection to Master at `192.168.122.100:18444`.

Step 2 — Chain comparison

The nodes exchanged information about their known chain, including headers.

Step 3 — Block transfer

Master supplied block data Amine needed to catch up.

Step 4 — Synchronization

Amine caught up through Block 103, according to the peer status.

The important principle is that the blockchain was synchronized through Bitcoin's peer-to-peer protocol, not by manually copying the block files.

## 6. How can we prevent this problem in the future?

For a lab, manually adding a peer is useful for learning and debugging. If you want Amine to reconnect to Master automatically after restarts, add this line to Amine's configuration file, inside the `[regtest]` section:

```
[regtest]
addnode=192.168.122.100:18444
```

If `[regtest]` already exists, add only the `addnode` line inside that existing section; do not create duplicate sections unnecessarily.

Restart Amine when appropriate, then verify:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getpeerinfo
```

And:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
```

Compare the block height and block hash with Master.

This configuration makes Master a peer Amine will try to connect to. It does not guarantee the connection will always succeed: Master must be running and reachable.

## Final summary

| Category              | Result                                                                                                    |
| --------------------- | --------------------------------------------------------------------------------------------------------- |
| Problem               | Amine was at Block 102 while Master was at Block 103.                                                     |
| Direct cause observed | Amine had no active P2P peers.                                                                            |
| Deeper cause          | Not conclusively determined.                                                                              |
| Consequence           | Amine could not retrieve Block 103 and could temporarily have a different view of confirmed transactions. |
| Solution              | Connected Amine to Master using `addnode`.                                                                |
| Evidence              | Peer information reported synchronized headers and blocks at height 103.                                  |
| Prevention            | Configure a persistent peer and verify synchronization after restarts.                                    |

### Questions to test your understanding

1. If Master shuts down after Amine receives Block 103, can Amine still read that block?
2. If Amine has no peers, can it independently create a new regtest block?
3. What is the difference between `addnode` and `rpcallowip`?
4. If Master and Amine both report height 103, why should we compare their block hashes as well?
5. If Amine restarts and loses its peer connection, does that automatically mean its blockchain data has been deleted?






# Answers: Bitcoin Regtest Node Synchronization

## Main question: Why can two Bitcoin nodes on the same regtest network temporarily have different block heights?

Two Bitcoin nodes can have different block heights because each node maintains its own local copy of the blockchain. If one node mines a new block and the other has not received it yet, their heights temporarily differ.

In your lab:

- Master has Block 103.
- Amine has Block 102.
- Amine has no peers, so it cannot receive Block 103 from Master.
- After Amine connects to Master, it downloads and validates the missing block, then advances to Block 103.

The difference is not automatically a sign of corruption. Nodes can temporarily have different views because of network delays, disconnected peers, or competing valid chains.

## Answers to all 12 questions

### 1. Does having zero peers automatically mean that a node's existing blockchain is invalid?

No. Zero peers means the node currently has no active P2P connections. It can still have a perfectly valid local blockchain and can read its existing blocks.

However, without peers, it cannot learn about new blocks from other nodes.

### 2. Why is `bestblockhash` useful when checking whether two nodes agree on the blockchain?

`bestblockhash` identifies the tip—the latest block—of the node's currently selected active chain.

For example:

```
Master:  height 103, hash ABC...
Amine:   height 103, hash XYZ...
```

Both nodes have height 103, but different hashes indicate that their active chains have different tip blocks.

If both height and `bestblockhash` match, their active chains agree at the tip. For stronger verification, compare earlier block hashes too.

### 3. If Amine reconnects to Master, what must happen before Amine advances from Block 102 to Block 103?

Amine must:

1. Establish a P2P connection to Master.
2. Discover that Master has a newer chain tip.
3. Request and receive the missing block data.
4. Validate Block 103, including its proof of work, transactions, and connection to Block 102.
5. Accept Block 103 into its active chain.

Once accepted, Amine's height advances to 103.

### 4. What is the difference between `synced_headers` and `synced_blocks`?

- `synced_headers` indicates the highest block-header height synchronized with that peer.
- `synced_blocks` indicates the highest block height for which the node reports having synchronized block data with that peer.

Headers contain metadata about blocks, including the previous block's hash and Merkle root. Full block data also includes the transactions.

A node may know about a block from its header before it has downloaded and validated the full block.

### 5. If Master disconnects, can Amine still read Block 103 from its local blockchain?

Yes, provided Amine has already received and retained Block 103. A peer is not required to read locally stored blocks.

For example:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockhash 103
```

This can work while Amine has no peers.

### 6. If Omar mines Block 104, how can Amine learn about it?

Omar must communicate the new block through Bitcoin's P2P network, directly or through other connected nodes.

The process is broadly:

1. Omar creates and broadcasts Block 104.
2. Connected peers learn about the block.
3. Amine receives the block or learns about it through block announcements and requests.
4. Amine validates the block.
5. If Block 104 extends Amine's selected active chain, Amine advances to height 104.

If Amine has no peers, it cannot receive Omar's announcement through P2P until it reconnects.

### 7. Why does Bitcoin use port `18444` for P2P in your regtest lab instead of mainnet's default port `8333`?

Bitcoin uses different default ports for different network environments.

| Network | Default P2P port |
| ------- | ---------------- |
| Mainnet | `8333`           |
| Regtest | `18444`          |

The separate ports help nodes distinguish network environments and reduce accidental connections between unrelated networks.

Your regtest chain is isolated from mainnet because it uses different network parameters and a different genesis block—not merely because it uses a different port.

### 8. If Master shuts down after Amine receives Block 103, can Amine still read that block?

Yes. Once Block 103 is stored locally, shutting down Master does not delete Amine's copy.

Amine can inspect the block using `getblock`, `getblockhash`, and other applicable RPC commands, even while disconnected.

### 9. If Amine has no peers, can it independently create a new regtest block?

Yes. Regtest allows Amine to generate blocks locally, without other peers, using a command such as:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf \
  generatetoaddress 1 "YOUR_REGTEST_ADDRESS"
```

However, if Amine and Master independently mine different blocks at the same height, they can temporarily have different chains. When they reconnect, Bitcoin's chain-selection rules determine which valid chain becomes active.

### 10. What is the difference between `addnode` and `rpcallowip`?

These settings operate at different network layers.

| Setting/command | Purpose                                                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `addnode`       | Establishes or requests a Bitcoin P2P connection to another node.                                                         |
| `rpcallowip`    | Controls which remote IP addresses are allowed to access the JSON-RPC server, subject to the other RPC security settings. |

For example:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf \
  addnode 192.168.122.100:18444 add
```

This connects Amine to Master for Bitcoin P2P communication.

By contrast, `rpcallowip` is related to remote administrative/API access. It does not connect blockchain peers, and you should not expose RPC to an untrusted network.

### 11. If Master and Amine both report height 103, why should we compare their block hashes as well?

Height only tells you the number of blocks in the selected chain. Two different blocks can both be at height 103.

For example:

```
Master:  height 103, hash 2c10e73d...
Amine:   height 103, hash 7ab45c91...
```

Different hashes indicate different block tips. They might reflect competing chains or a different chain history.

In your lab, Block 103's expected hash is:

```
2c10e73d2eeb5b8856c31ca27a5def38b52616c899fad26812a8bd04974cba9d
```

Check it on both nodes:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockhash 103
```

Matching hashes at the tip are stronger evidence of agreement than matching heights alone.

### 12. If Amine restarts and loses its peer connection, does that automatically mean its blockchain data has been deleted?

No. Restarting Bitcoin Core and losing a P2P connection are different events from deleting blockchain data.

- A restart stops and starts the node process.
- A lost peer connection means the node is disconnected from that peer.
- Deleting or changing the data directory can cause the node to use different or missing local blockchain data.

After a restart, check:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getpeerinfo
```

If the block height remains 103 but `getpeerinfo` is empty, the local chain may still be intact; only the connection is missing.

## Practical verification for your lab

Run these commands on both Master and Amine:

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockchaininfo
```

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getblockhash 103
```

```
bitcoin-cli -conf=/opt/bitcoin/bitcoin.conf getpeerinfo
```

Compare the outputs:

- Height: Are both nodes at 103?
- Best block hash: Do both report the same tip?
- Peers: Are the nodes actually connected?

These three checks help distinguish local blockchain state from network connectivity.

## Questions to test yourself

1. If two nodes have the same `bestblockhash`, must their peer lists also be identical?
2. Can a node have valid block headers but still be missing the corresponding full block data?
3. If Amine mines Block 104 while disconnected from Master, what happens when the two nodes reconnect and discover competing chains?



### how the peer to peer connection is established between the nodes
# Bitcoin P2P Connections — `getpeerinfo`

To see the P2P (Peer-to-Peer) connections that your Bitcoin node has, use `getpeerinfo` with `bitcoin-cli`.

Since you're using Bitcoin Core 31.1 on Ubuntu and working with a `regtest` network, the following commands will help you inspect your connected peers.

## 1. See All P2P Connections

Run:

```
/opt/bitcoin/bin/bitcoin-cli -regtest getpeerinfo
```

If `bitcoin-cli` is already in your `PATH`, you can use:

```
bitcoin-cli -regtest getpeerinfo
```

This command returns a JSON array containing information about every peer currently connected to your node.

If no peers are connected, the result will be an empty array:

```
[]
```

## 2. Understand the Output

The `getpeerinfo` command returns several fields describing each connection.

| Field             | Meaning                                                                                   |
| ----------------- | ----------------------------------------------------------------------------------------- |
| `id`              | Internal identifier of the peer connection.                                               |
| `addr`            | IP address and port of the connected peer.                                                |
| `inbound`         | `true` if the peer connected to your node; `false` if your node initiated the connection. |
| `conntime`        | Unix timestamp when the connection began.                                                 |
| `version`         | Bitcoin P2P protocol version used by the peer.                                            |
| `subver`          | Software version string reported by the peer.                                             |
| `startingheight`  | Block height reported by the peer during connection setup.                                |
| `synced_headers`  | Highest block-header height known from that peer, as reported by your node.               |
| `synced_blocks`   | Highest block height known from that peer, as reported by your node.                      |
| `bytesrecv`       | Total bytes received from the peer.                                                       |
| `bytessent`       | Total bytes sent to the peer.                                                             |
| `connection_type` | Type of connection, such as `outbound-full-relay`.                                        |

Important: `getpeerinfo` shows the connections your node currently has, not every Bitcoin node in the network.

## 3. Useful Commands for Your Lab

### 3.1. Check the Number of Connected Peers

```
bitcoin-cli -regtest getconnectioncount
```

Example output:

```
2
```

This means your node currently has two P2P connections.

### 3.2. Display Peer Information in Readable JSON

```
bitcoin-cli -regtest getpeerinfo | python3 -m json.tool
```

This formats the JSON output with indentation, making it easier to read.

### 3.3. Check Your Node's Network Configuration

```
bitcoin-cli -regtest getnetworkinfo
```

This displays network-related information, including protocol details and local addresses.

### 3.4. Check Your Local Blockchain Height

```
bitcoin-cli -regtest getblockchaininfo
```

Look for fields such as:

- `blocks`: number of blocks in the active blockchain.
- `headers`: number of headers your node has received and validated.
- `bestblockhash`: hash of the latest block in your active chain.

## 4. Connect Your Bitcoin Nodes Manually

In your Ubuntu/KVM lab, suppose Omar runs a miner node and Amine wants to connect to it.

Assume Omar's VM has an IP address of `192.168.122.101` and listens on the default regtest P2P port, `18444`.

On Amine's node, run:

```
bitcoin-cli -regtest addnode "192.168.122.101:18444" "onetry"
```

Replace the example IP address with Omar's actual VM IP address.

The `onetry` option attempts to establish a connection without adding a persistent peer configuration.

After running the command, check the connection:

```
bitcoin-cli -regtest getpeerinfo
```

Or check the number of connected peers:

```
bitcoin-cli -regtest getconnectioncount
```

Important: For this connection to work:

1. Omar's Bitcoin node must be running.
2. Omar's node must listen on a network interface reachable from Amine's VM.
3. The VM network and firewall must allow TCP connections to port `18444`.
4. Both nodes must use compatible network settings and the intended regtest network.

The default Bitcoin Core regtest P2P port is `18444`, unless you configure a different port.

## 5. Understand How the P2P Network Works

Consider this example topology for your lab:

```
Omar (Miner Node)
       |
       | P2P connection
       |
Amine (Bitcoin Node)
       |
       | P2P connection
       |
Sara (Bitcoin Node)
```

This is an illustrative topology. Your actual connections depend on how you configure the nodes.

Bitcoin uses a decentralized P2P network. Each node communicates with its connected peers to exchange information about transactions and blocks.

For example, when Omar mines a valid block:

1. Omar mines the block. His node constructs a candidate block and performs proof of work.
2. Omar validates and accepts the block locally. The block must satisfy Bitcoin's consensus rules.
3. Omar announces the block to connected peers. The peers learn about the new block.
4. Connected nodes validate the block. They check its proof of work, transactions, and other consensus requirements.
5. The block propagates through the network. Nodes can relay it to their own peers.

If Amine is connected to Omar, Amine can receive the block announcement. If Amine is also connected to Sara, Sara may subsequently learn about the block through Amine.

However, propagation is not guaranteed to follow one exact path. Bitcoin nodes may have several peers, and a block can reach a node through different connections.

## 6. Troubleshooting P2P Connections

If `getconnectioncount` returns `0`, check the following:

```
bitcoin-cli -regtest getconnectioncount
bitcoin-cli -regtest getpeerinfo
bitcoin-cli -regtest getnetworkinfo
```

Then verify that Omar's node is listening on the expected port:

```
ss -lntp | grep 18444
```

You can also check whether the port is reachable from Amine's VM:

```
nc -vz 192.168.122.101 18444
```

Replace the IP address with Omar's actual VM IP.

Remember that zero peers does not mean your existing blockchain is invalid. It means your node currently has no active P2P connections. Your node can still have a valid local blockchain while disconnected from other nodes.

## 7. Practice Questions

1. What is the difference between `inbound: true` and `inbound: false`?
2. If `getconnectioncount` returns `0`, does that mean your blockchain is invalid?
3. If Omar has 101 blocks and Amine has 100 blocks, which commands would you use to investigate the difference?
4. If Omar mines a block while Amine is disconnected, how might Amine receive that block after reconnecting?
5. What is the difference between `addnode ... onetry` and configuring a persistent peer connection?