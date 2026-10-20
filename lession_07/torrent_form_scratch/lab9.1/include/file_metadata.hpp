#ifndef FILE_METADATA_HPP
#define FILE_METADATA_HPP

#include <cstdint>
#include <string>

struct FileMetadata {
    std::string filename;
    std::uint64_t file_size;
    std::uint32_t piece_size;
    std::uint32_t total_pieces;
};

std::uint32_t calculate_total_pieces(
    std::uint64_t file_size,
    std::uint32_t piece_size
);

#endif