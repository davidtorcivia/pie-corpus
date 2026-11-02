#!/usr/bin/env bash
# Build the VTL 2.4 API as a shared library (Linux/macOS) from the VTL 2.4 release zip.
#   ./build_vtl24.sh /path/to/VTL2.4.zip      → libvtl24.so next to this script
# On Windows you don't need this: copy API/VocalTractLabApi.dll (+ msvcp140.dll, vcruntime140*.dll)
# from the zip next to vtlengine.py.
set -euo pipefail
ZIP="${1:?usage: build_vtl24.sh VTL2.4.zip}"
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
python3 -c "import zipfile,sys; z=zipfile.ZipFile(sys.argv[1]); [z.extract(n, sys.argv[2]) for n in z.namelist() if n.startswith('API/Developer/Sources/')]" "$ZIP" "$TMP"
SRC="$TMP/API/Developer/Sources"
# Tube.h declares a C++17 inline constexpr array; the sources need C++14 (dynamic exception specs)
printf '#include "Tube.h"\nconstexpr int Tube::SINUS_COUPLING_SECTION[];\n' > "$TMP/fix_constexpr.cpp"
EXT=so; [[ "$(uname)" == Darwin ]] && EXT=dylib
g++ -O2 -fPIC -shared -std=c++14 -DNDEBUG -w -I"$SRC" \
    $(ls "$SRC"/*.cpp | grep -v SoundLib.cpp) "$TMP/fix_constexpr.cpp" -o "$HERE/libvtl24.$EXT"
rm -rf "$TMP"
echo "built $HERE/libvtl24.$EXT"
