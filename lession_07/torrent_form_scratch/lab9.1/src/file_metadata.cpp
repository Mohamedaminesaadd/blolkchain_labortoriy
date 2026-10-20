#include "file_metadata.hpp"

#include <stdexcept>

std::uint32_t calculate_total_pieces(
    std::uint64_t file_size,
    std::uint32_t piece_size
) {
    if (piece_size == 0) {
        throw std::invalid_argument(
            "Piece size cannot be zero"
        );
    }

    if (file_size == 0) {
        return 0;
    }

    const std::uint64_t count =
        1 + (file_size - 1) / piece_size;

    if (count > UINT32_MAX) {
        throw std::overflow_error(
            "Too many pieces for uint32_t"
        );
    }

    return static_cast<std::uint32_t>(count);
}