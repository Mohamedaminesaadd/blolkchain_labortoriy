cmake_minimum_required(VERSION 3.16)

project(P2PProtocol LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(protocol_test
    main.cpp
    protocol.cpp
)

target_compile_options(protocol_test PRIVATE
    -Wall
    -Wextra
    -Wpedantic
)