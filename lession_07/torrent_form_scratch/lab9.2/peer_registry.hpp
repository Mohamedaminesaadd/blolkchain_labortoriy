
#ifndef PEER_REGISTRY_HPP
#define PEER_REGISTRY_HPP

#include "peer_identity.hpp"

#include <unordered_map>
#include <vector>
#include <string>
#include <cstddef>

class PeerRegistry {
private:
    // Key: peer ID. Value: peer information.
    std::unordered_map<std::string, PeerIdentity> peers;

public:
    // Register a new peer.
    bool addPeer(const PeerIdentity& peer) {
        auto result = peers.emplace(peer.peer_id, peer);
        return result.second;
    }

    // Find a peer by ID.
    const PeerIdentity* findPeer(
        const std::string& peer_id
    ) const {
        auto it = peers.find(peer_id);

        if (it == peers.end()) {
            return nullptr;
        }

        return &it->second;
    }

    // Remove a peer by ID.
    bool removePeer(const std::string& peer_id) {
        return peers.erase(peer_id) > 0;
    }

    // Return all registered peers.
    std::vector<PeerIdentity> getAllPeers() const {
        std::vector<PeerIdentity> result;
        result.reserve(peers.size());

        for (const auto& entry : peers) {
            result.push_back(entry.second);
        }

        return result;
    }

    // Return the number of peers.
    std::size_t size() const {
        return peers.size();
    }

    // Check whether the registry is empty.
    bool empty() const {
        return peers.empty();
    }
};

#endif
