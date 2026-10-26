
#include <iostream>

#include "peer_identity.hpp"
#include "peer_registry.hpp"

int main() {
    PeerRegistry registry;

    // 1. Create peers.
    PeerIdentity peer1("peer-001", "192.168.1.10", 5001);
    PeerIdentity peer2("peer-002", "192.168.1.11", 5002);
    PeerIdentity peer3("peer-003", "192.168.1.12", 5003);

    // 2. Register peers.
    std::cout << "=== Registering peers ===\n";

    std::cout << std::boolalpha;

    std::cout << "Peer 1 added: "
              << registry.addPeer(peer1) << '\n';

    std::cout << "Peer 2 added: "
              << registry.addPeer(peer2) << '\n';

    std::cout << "Peer 3 added: "
              << registry.addPeer(peer3) << '\n';

    // 3. Display the number of peers.
    std::cout << "\nTotal peers: "
              << registry.size() << '\n';

    // 4. Search for a peer.
    std::cout << "\n=== Searching for peer-002 ===\n";

    const PeerIdentity* found =
        registry.findPeer("peer-002");

    if (found != nullptr) {
        found->display();
    } else {
        std::cout << "Peer not found\n";
    }

    // 5. Test duplicate registration.
    std::cout << "\n=== Testing duplicate registration ===\n";

    bool added = registry.addPeer(
        PeerIdentity("peer-002", "10.0.0.5", 6000)
    );

    std::cout << "Duplicate added: " << added << '\n';

    // 6. Display all registered peers.
    std::cout << "\n=== All registered peers ===\n";

    for (const auto& peer : registry.getAllPeers()) {
        peer.display();
        std::cout << "--------------------\n";
    }

    // 7. Remove a peer.
    std::cout << "\n=== Removing peer-003 ===\n";

    bool removed = registry.removePeer("peer-003");

    std::cout << "Peer removed: " << removed << '\n';

    // 8. Display the final state.
    std::cout << "\n=== Final registry state ===\n";

    std::cout << "Remaining peers: "
              << registry.size() << '\n';

    std::cout << "Registry empty: "
              << registry.empty() << '\n';

    return 0;
}
