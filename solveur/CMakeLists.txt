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
set(ZLIB OFF CACHE BOOL "" FORCE)   # pas de lecture de fichiers compresses ; evite libz.so dans le lien statique
add_subdirectory(HiGHS EXCLUDE_FROM_ALL)

add_executable(placement src/placement.cpp)
target_include_directories(placement PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})   # json.hpp
target_link_libraries(placement PRIVATE highs)
if(NOT MSVC)
  target_link_options(placement PRIVATE -s)   # binaire strippe
endif()
option(PLACEMENT_STATIC "Binaire Linux entierement statique (releases, Cloud Functions)" OFF)
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND NOT APPLE)
  if(PLACEMENT_STATIC)
    target_link_options(placement PRIVATE -static)
  else()
    target_link_options(placement PRIVATE -static-libstdc++ -static-libgcc)   # portable entre distributions Linux
  endif()
endif()
