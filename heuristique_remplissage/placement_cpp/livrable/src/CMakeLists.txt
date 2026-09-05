cmake_minimum_required(VERSION 3.16)
project(placement_paras CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# HiGHS embarque (sources clonees par build.sh dans ./HiGHS)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(FAST_BUILD ON CACHE BOOL "" FORCE)
set(HIGHS_NO_DEFAULT_THREADS ON CACHE BOOL "" FORCE)
add_subdirectory(HiGHS EXCLUDE_FROM_ALL)

add_executable(placement placement.cpp)
target_include_directories(placement PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(placement PRIVATE highs)
target_link_options(placement PRIVATE -s)   # binaire strippe
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND NOT APPLE)
  target_link_options(placement PRIVATE -static-libstdc++ -static-libgcc)   # portable entre distributions Linux
endif()
