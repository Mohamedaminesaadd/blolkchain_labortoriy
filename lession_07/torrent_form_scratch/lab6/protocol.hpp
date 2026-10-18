#ifndef PROTOCOL_HPP
#define PROTOCOL_HPP

#include <cstddef>
#include <cstdint>
#include <vector>

namespace p2p {

// Protocol identification
constexpr std::uint32_t MAGIC = 0x50325031; // "P2P1"

// Protocol version
constexpr std::uint8_t VERSION = 1;

// Message header field sizes
constexpr std::size_t MAGIC_SIZE = 4;
constexpr std::size_t VERSION_SIZE = 1;
constexpr std::size_t TYPE_SIZE = 1;
constexpr std::size_t MESSAGE_ID_SIZE = 8;
constexpr std::size_t LENGTH_SIZE = 4;

// Total fixed header size: 18 bytes
constexpr std::size_t HEADER_SIZE =
    MAGIC_SIZE +
    VERSION_SIZE +
    TYPE_SIZE +
    MESSAGE_ID_SIZE +
    LENGTH_SIZE;

// Maximum payload: 1 MiB
constexpr std::uint32_t MAX_PAYLOAD_SIZE = 1024 * 1024;

// Message types
enum class MessageType : std::uint8_t {
    PING = 1,
    PONG = 2,
    DATA = 3
};

// Logical representation of a message
struct Message {
    MessageType type;
    std::uint64_t id;
    std::vector<std::uint8_t> payload;
};

// Serialize a message into bytes
std::vector<std::uint8_t> serialize(const Message& message);

// Deserialize bytes into one complete message
Message deserialize(const std::vector<std::uint8_t>& bytes);

} // namespace p2p

#endif // PROTOCOL_HPP