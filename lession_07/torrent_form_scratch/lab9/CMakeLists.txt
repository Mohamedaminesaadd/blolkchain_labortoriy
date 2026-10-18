cmake_minimum_required(VERSION 3.16)
project(lab9 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

add_executable(lab9 main.cpp sha256.hpp)

if(MSVC)
    target_compile_options(lab9 PRIVATE /W4)
else()
    target_compile_options(lab9 PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Next stage (peers exchanging pieces over TCP): uncomment when we add Boost.Asio
# find_package(Boost REQUIRED COMPONENTS system)
# target_link_libraries(lab9 PRIVATE Boost::system)