#include "protocol.hpp"

#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace p2p;

void test_round_trip() {
    std::string text = "Hello from Amine";

    std::vector<std::uint8_t> payload(
        text.begin(), text.end()
    );

    Message original{
        MessageType::DATA,
        123456789,
        payload
    };

    // Serialize the message.
    std::vector<std::uint8_t> bytes = serialize(original);

    // Deserialize the bytes.
    Message decoded = deserialize(bytes);

    // Verify that the original message was preserved.
    assert(decoded.type == original.type);
    assert(decoded.id == original.id);
    assert(decoded.payload == original.payload);

    std::cout << "[PASS] Serialization round trip\n";
}

void test_empty_payload() {
    Message original{
        MessageType::PING,
        1,
        {}
    };

    auto bytes = serialize(original);
    Message decoded = deserialize(bytes);

    assert(bytes.size() == HEADER_SIZE);
    assert(decoded.type == MessageType::PING);
    assert(decoded.id == 1);
    assert(decoded.payload.empty());

    std::cout << "[PASS] Empty payload\n";
}

void test_invalid_magic() {
    Message message{MessageType::PING, 2, {}};
    auto bytes = serialize(message);

    bytes[0] ^= 0xFF;

    bool rejected = false;

    try {
        deserialize(bytes);
    } catch (const std::runtime_error&) {
        rejected = true;
    }

    assert(rejected);

    std::cout << "[PASS] Invalid magic rejected\n";
}

void test_truncated_header() {
    std::vector<std::uint8_t> bytes = {0x50, 0x32, 0x50};

    bool rejected = false;

    try {
        deserialize(bytes);
    } catch (const std::runtime_error&) {
        rejected = true;
    }

    assert(rejected);

    std::cout << "[PASS] Truncated header rejected\n";
}

void test_unknown_type() {
    Message message{MessageType::PING, 3, {}};
    auto bytes = serialize(message);

    bytes[5] = 99;

    bool rejected = false;

    try {
        deserialize(bytes);
    } catch (const std::runtime_error&) {
        rejected = true;
    }

    assert(rejected);

    std::cout << "[PASS] Unknown message type rejected\n";
}

void test_payload_length_mismatch() {
    Message message{MessageType::DATA, 4, {'A', 'B', 'C'}};
    auto bytes = serialize(message);

    // The actual payload contains 3 bytes.
    // Change the declared payload length to 2.
    bytes[17] = 2;

    bool rejected = false;

    try {
        deserialize(bytes);
    } catch (const std::runtime_error&) {
        rejected = true;
    }

    assert(rejected);

    std::cout << "[PASS] Payload length mismatch rejected\n";
}

int main() {
    try {
        test_round_trip();
        test_empty_payload();
        test_invalid_magic();
        test_truncated_header();
        test_unknown_type();
        test_payload_length_mismatch();

        std::cout << "\nAll protocol tests passed!\n";
    } catch (const std::exception& e) {
        std::cerr << "Unexpected error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}