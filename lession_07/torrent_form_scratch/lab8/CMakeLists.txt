
cmake_minimum_required(VERSION 3.16)

project(Lab8FileTransfer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Boost REQUIRED COMPONENTS system)

add_executable(server server.cpp)
add_executable(client client.cpp)

target_link_libraries(server PRIVATE Boost::system)
target_link_libraries(client PRIVATE Boost::system)
