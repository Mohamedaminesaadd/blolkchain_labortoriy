# Peer Discovery with a Central Tracker — C++ P2P Lab 10

In your C++ torrent-like file-sharing project, you already have two important components:

- `PeerIdentity`: describes a peer using its ID, IP address, and port.
- `PeerRegistry`: stores and manages known peers.

The next step is Peer Discovery: how does one peer find other peers when it doesn't already know their IP addresses?

A common solution is a central tracker.

## 1. What is a central tracker?

A central tracker is a server that helps peers find one another. It keeps a list of peers participating in a particular file-sharing swarm.

The tracker usually does not transfer the files themselves. Instead, peers contact the tracker to discover other peers, then communicate directly to exchange file data.

[🚀 Understanding Peer-to-Peer (P2P) File Sharing: How Peers Work Together to Build the Whole](https://images.openai.com/static-rsc-4/Np6ennPhT2D1UWdN1TEfUjVXU4tBO2VHtxvLXBikIcLdfmIwBNtdAxR952zzoMogiAKpHZIJx_iV2ElBWJ0Ymd79yjXeuIkEcMblyj8YvRTsuW5MwP1DnySiUUsBXYz-1qMUYFNHNkuBwPutJXaGi8JKZmp0G361NjJGV61kn30?purpose=inline)

[linkedin.com](https://www.linkedin.com/pulse/understanding-peer-to-peer-p2p-file-sharing-how-peers-zimmendra-mhnsc?utm_source=chatgpt.com)

Imagine three computers want to share the same file:

- Peer A has the file.
- Peer B wants to download the file.
- Peer C also has the file.

Peer B knows the tracker's address but doesn't know Peer A or Peer C.

The tracker helps Peer B discover them.

## 2. How peer discovery works

Peer B

Wants to download a file

Central Tracker

Stores the peer list for the requested file

Peer A and Peer C

Tracker returns their advertised endpoints

Direct P2P connections

Peers exchange file chunks without routing the file through the tracker

The process has five steps.

1. Announce: Peer A tells the tracker that it is participating in a particular file's swarm.
2. Register: The tracker records Peer A's identity and advertised network endpoint.
3. Request peers: Peer B asks the tracker for peers sharing the same file.
4. Return peers: The tracker returns a list of available peer endpoints.
5. Connect: Peer B attempts to establish direct TCP connections to the discovered peers.

The tracker is the discovery mechanism, while your peer connection manager handles the actual network connections.

## 3. What information does the tracker store?

In a real torrent system, the tracker groups peers by the identifier of the file they want to share. BitTorrent uses an `info_hash` to identify a torrent's swarm.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.bittorrent.org\&sz=32)

bittorrent.org

+1



For your learning project, we can simplify this to a `file_id`.

For example:

```
Central Tracker
│
├── file_A
│   ├── peer-001 → 192.168.1.10:5001
│   └── peer-002 → 192.168.1.11:5002
│
└── file_B
    ├── peer-002 → 192.168.1.11:5002
    └── peer-003 → 192.168.1.12:5003
```

Notice that `peer-002` participates in both swarms.

This is why a simple global `PeerRegistry` is not enough for a tracker that supports multiple files. The tracker needs to associate each peer with the file or swarm it participates in.

## 4. What messages do peers send?

For your own protocol, start with three logical messages:

| Message     | Purpose                                                        |
| ----------- | -------------------------------------------------------------- |
| `ANNOUNCE`  | Tell the tracker that this peer participates in a file's swarm |
| `GET_PEERS` | Ask the tracker for other peers sharing that file              |
| `LEAVE`     | Tell the tracker that the peer is leaving the swarm            |

Example:

Peer A → Tracker

`ANNOUNCE(file_A, peer-A, port=5001)`

Register Peer A for file A.

Peer B → Tracker

`GET_PEERS(file_A)`

Request the peers associated with file A.

Tracker → Peer B

`PEERS(peer-A, 192.168.1.10, 5001)`

Return the known peer endpoints.

Real BitTorrent trackers use a standardized announce protocol with fields such as `info_hash`, `peer_id`, and `port`; your simplified messages are for learning, not wire-compatible with BitTorrent.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://bittorrent.org\&sz=32)

bittorrent.org

+1



## 5. How should you implement it in C++?

For your current project, I recommend building it in two stages.

Stage 1 — Simulate the tracker locally

Create a `CentralTracker` class that maintains a map from file IDs to lists of `PeerIdentity` objects.

It should provide methods such as:

```
bool announce(const std::string& file_id,
              const PeerIdentity& peer);

std::vector<PeerIdentity> getPeers(
    const std::string& file_id,
    const std::string& requester_id
);
```

The tracker should exclude the requesting peer from its returned list and avoid duplicate registrations.

At this stage, everything runs inside one process. You can test the discovery logic without dealing with sockets.

Stage 2 — Make the tracker a real server

Once the simulation works:

1. Run the tracker as a TCP server.
2. Make peers send `ANNOUNCE` and `GET_PEERS` messages over TCP.
3. Serialize and parse messages using your existing binary protocol.
4. Convert returned peer information into `PeerIdentity` objects.
5. Add discovered peers to the local `PeerRegistry`.
6. Use Boost.Asio to connect directly to discovered peers.

One important limitation: returning an IP address and port doesn't guarantee that the peer is reachable. Firewalls, NAT, and offline peers can prevent direct connections.

## 6. Central tracker versus decentralized discovery

A central tracker is a good starting point because it is easier to implement and debug. However, it introduces a single point of failure: if the tracker goes offline, new peers may be unable to discover one another through it.

A decentralized alternative is a distributed hash table (DHT), where peers collectively maintain discovery information rather than depending on one central server. BitTorrent's DHT specification describes this approach.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.bittorrent.org\&sz=32)

bittorrent.org

+1



Your next lab should be: implement the `CentralTracker` class using your existing `PeerIdentity` and `PeerRegistry` concepts, then test two or three peers sharing the same file before adding networking.