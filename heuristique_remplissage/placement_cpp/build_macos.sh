#!/bin/sh
# Compilation croisee macOS (arm64 et x86_64) avec zig cc, sans Mac ni SDK : zig embarque
# les en-tetes et stubs de libc macOS. Produit livrable/placement-macos-arm64 et -x86_64.
# Non teste sur Mac ici : a verifier avec `./placement-macos-arm64 --help`.
# Reutilise la liste des sources HiGHS et le HConfig.h generes par le build Linux (./build).
set -u
cd "$(dirname "$0")"
ZIG=${ZIG:-zig}
OUT=${OUT:-livrable}
mkdir -p "$OUT"
# sources reellement compilees par le build Linux (chemins absolus dans build.ninja)
# HiGHS 1.9.0 inclut immintrin.h (x86) sans garde : neutralise sur ARM
grep -q PLACEMENT_ARM_PATCH HiGHS/src/parallel/HighsSpinMutex.h || python3 - <<'PY'
from pathlib import Path
h = Path('HiGHS/src/parallel/HighsSpinMutex.h'); s = h.read_text()
s = s.replace('#include <immintrin.h>', '#if defined(__x86_64__) || defined(__i386__) || defined(_M_X64)\n#include <immintrin.h>\n#else\n/* PLACEMENT_ARM_PATCH */\nstatic inline void _mm_pause() {}\n#endif', 1)
h.write_text(s)
PY
SRCS=$(grep -oE "$(pwd)/HiGHS/[^ ]*\.(cpp|cc|c)( |$)" build/build.ninja | sed "s#$(pwd)/##; s/ *$//" | sort -u)
INC="-IHiGHS/src -IHiGHS/src/util -IHiGHS/src/lp_data -IHiGHS/src/io -IHiGHS/src/ipm -IHiGHS/src/ipm/ipx -IHiGHS/src/ipm/basiclu -IHiGHS/src/mip -IHiGHS/src/model -IHiGHS/src/parallel -IHiGHS/src/pdlp -IHiGHS/src/presolve -IHiGHS/src/qpsolver -IHiGHS/src/simplex -IHiGHS/src/test -IHiGHS/src/interfaces -IHiGHS/src/pdlp/cupdlp -IHiGHS/extern -IHiGHS/extern/filereaderlp -IHiGHS/extern/pdqsort -IHiGHS/extern/zstr -Ibuild/HiGHS -Ibuild -I."
for T in x86_64-macos aarch64-macos; do
  echo "== $T"
  OBJ=build-macos-$T; mkdir -p "$OBJ"
  # .c en C (basiclu, cupdlp), .cc et .cpp en C++17
  echo "$SRCS" | xargs -P "$(nproc 2>/dev/null || echo 4)" -I{} sh -c 'f={}; case "$f" in *.c) $0 cc -target $1 -O2 -w -DNDEBUG $2 -c "$f" -o "$3/$(echo "$f" | tr / _).o" ;; *) $0 c++ -target $1 -O2 -std=c++17 -w -DNDEBUG $2 -c "$f" -o "$3/$(echo "$f" | tr / _).o" ;; esac' "$ZIG" "$T" "$INC" "$OBJ"
  $ZIG ar rcs "$OBJ/libhighs.a" "$OBJ"/*.o || { echo "echec $T"; continue; }
  $ZIG c++ -target $T -O2 -std=c++17 -w $INC placement.cpp "$OBJ/libhighs.a" -o "$OUT/placement-macos-${T%-macos}"
  ls -la "$OUT/placement-macos-${T%-macos}" || echo "echec edition de liens $T"
done
