
#ifndef PEER_IDENTITY_HPP
#define PEER_IDENTITY_HPP

#include <string>
#include <cstdint>
#include <iostream>

struct PeerIdentity {
    std::string peer_id;
    std::string ip_address;
    std::uint16_t port;

    PeerIdentity(
        const std::string& id,
        const std::string& ip,
        std::uint16_t p
    )
        : peer_id(id),
          ip_address(ip),
          port(p) {}

    std::string endpoint() const {
        return ip_address + ":" + std::to_string(port);
    }

    void display() const {
        std::cout << "Peer ID: " << peer_id << '\n';
        std::cout << "Address: " << endpoint() << '\n';
    }
};

#endif
