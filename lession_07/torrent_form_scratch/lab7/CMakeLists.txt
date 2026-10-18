
cmake_minimum_required(VERSION 3.16)

project(Lab7FileHandling LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(file_copy main.cpp)

target_compile_options(file_copy PRIVATE
    -Wall
    -Wextra
    -Wpedantic
)
