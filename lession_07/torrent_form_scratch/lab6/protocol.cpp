#include "protocol.hpp"

#include <stdexcept>
#include <utility>

namespace p2p {

namespace {

// Append a 32-bit integer in big-endian order.
void append_u32(std::vector<std::uint8_t>& out,
                std::uint32_t value) {
    out.push_back(static_cast<std::uint8_t>(value >> 24));
    out.push_back(static_cast<std::uint8_t>(value >> 16));
    out.push_back(static_cast<std::uint8_t>(value >> 8));
    out.push_back(static_cast<std::uint8_t>(value));
}

// Append a 64-bit integer in big-endian order.
void append_u64(std::vector<std::uint8_t>& out,
                std::uint64_t value) {
    for (int shift = 56; shift >= 0; shift -= 8) {
        out.push_back(
            static_cast<std::uint8_t>(value >> shift)
        );
    }
}

// Read a 32-bit integer from the given offset.
std::uint32_t read_u32(
    const std::vector<std::uint8_t>& bytes,
    std::size_t offset
) {
    return
        (static_cast<std::uint32_t>(bytes[offset]) << 24) |
        (static_cast<std::uint32_t>(bytes[offset + 1]) << 16) |
        (static_cast<std::uint32_t>(bytes[offset + 2]) << 8) |
        static_cast<std::uint32_t>(bytes[offset + 3]);
}

// Read a 64-bit integer from the given offset.
std::uint64_t read_u64(
    const std::vector<std::uint8_t>& bytes,
    std::size_t offset
) {
    std::uint64_t value = 0;

    for (std::size_t i = 0; i < 8; ++i) {
        value = (value << 8) | bytes[offset + i];
    }

    return value;
}

// Validate the message type before serialization.
bool is_valid_type(MessageType type) {
    switch (type) {
        case MessageType::PING:
        case MessageType::PONG:
        case MessageType::DATA:
            return true;

        default:
            return false;
    }
}

} // anonymous namespace


// =====================================================
// SERIALIZATION
// =====================================================

std::vector<std::uint8_t> serialize(const Message& message) {

    // 1. Validate message type.
    if (!is_valid_type(message.type)) {
        throw std::invalid_argument("Invalid message type");
    }

    // 2. Validate payload size.
    if (message.payload.size() > MAX_PAYLOAD_SIZE) {
        throw std::length_error("Payload exceeds maximum size");
    }

    std::vector<std::uint8_t> out;

    out.reserve(HEADER_SIZE + message.payload.size());

    // 3. Magic number: 4 bytes.
    append_u32(out, MAGIC);

    // 4. Protocol version: 1 byte.
    out.push_back(VERSION);

    // 5. Message type: 1 byte.
    out.push_back(static_cast<std::uint8_t>(message.type));

    // 6. Message ID: 8 bytes.
    append_u64(out, message.id);

    // 7. Payload length: 4 bytes.
    append_u32(
        out,
        static_cast<std::uint32_t>(message.payload.size())
    );

    // 8. Payload: variable length.
    out.insert(
        out.end(),
        message.payload.begin(),
        message.payload.end()
    );

    return out;
}


// =====================================================
// DESERIALIZATION
// =====================================================

Message deserialize(const std::vector<std::uint8_t>& bytes) {

    // 1. Check that the complete fixed header exists.
    if (bytes.size() < HEADER_SIZE) {
        throw std::runtime_error("Incomplete message header");
    }

    // 2. Validate the magic number.
    if (read_u32(bytes, 0) != MAGIC) {
        throw std::runtime_error("Invalid magic number");
    }

    // 3. Validate the protocol version.
    if (bytes[4] != VERSION) {
        throw std::runtime_error("Unsupported protocol version");
    }

    // 4. Decode the message type.
    MessageType type;

    switch (bytes[5]) {
        case static_cast<std::uint8_t>(MessageType::PING):
            type = MessageType::PING;
            break;

        case static_cast<std::uint8_t>(MessageType::PONG):
            type = MessageType::PONG;
            break;

        case static_cast<std::uint8_t>(MessageType::DATA):
            type = MessageType::DATA;
            break;

        default:
            throw std::runtime_error("Unknown message type");
    }

    // 5. Read message ID and payload length.
    const std::uint64_t id = read_u64(bytes, 6);
    const std::uint32_t payload_length = read_u32(bytes, 14);

    // 6. Reject payloads exceeding the protocol limit.
    if (payload_length > MAX_PAYLOAD_SIZE) {
        throw std::runtime_error("Payload exceeds maximum size");
    }

    // 7. Validate the complete message length.
    // Subtraction avoids overflow in HEADER_SIZE + payload_length.
    if (bytes.size() - HEADER_SIZE != payload_length) {
        throw std::runtime_error(
            "Message size does not match payload length"
        );
    }

    // 8. Extract the payload.
    std::vector<std::uint8_t> payload(
        bytes.begin() + HEADER_SIZE,
        bytes.end()
    );

    // 9. Return the reconstructed message.
    return Message{type, id, std::move(payload)};
}

} // namespace p2p