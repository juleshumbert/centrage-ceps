#!/bin/sh
# Construit placement_cpp/placement avec HiGHS embarque.
#   ./build.sh                 (compilateur du systeme : g++ ou clang++, cmake, ninja ou make)
#   CC=zigcc CXX=zigcxx ./build.sh   (compilateur alternatif, ex. zig cc sans compilateur C installe)
#   PLACEMENT_STATIC=1 ./build.sh   (Linux : binaire entierement statique, releases et Cloud Functions)
# Sources : HiGHS v1.9.0 (MIT) clone dans ./HiGHS, nlohmann/json 3.11.3 (MIT) dans ./json.hpp.
set -e
cd "$(dirname "$0")"
[ -d HiGHS ] || git clone -q --depth 1 --branch v1.9.0 https://github.com/ERGO-Code/HiGHS.git HiGHS
[ -f json.hpp ] || curl -sL -o json.hpp https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp
GEN=""
command -v ninja >/dev/null 2>&1 && GEN="-G Ninja"
cmake -S . -B build $GEN -DCMAKE_BUILD_TYPE=Release ${PLACEMENT_STATIC:+-DPLACEMENT_STATIC=ON} ${CC:+-DCMAKE_C_COMPILER=$CC} ${CXX:+-DCMAKE_CXX_COMPILER=$CXX}
cmake --build build --target placement -j "$(nproc 2>/dev/null || echo 4)"
ls -la build/placement
