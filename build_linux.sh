#!/usr/bin/env bash
set -euo pipefail

# If VCPKG_ROOT is set and contains a real vcpkg, use it (pins Boost 1.83).
# Otherwise, create a stub that uses system packages.
if [ -n "${VCPKG_ROOT:-}" ] && [ -f "${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" ]; then
    echo "Using vcpkg from VCPKG_ROOT=${VCPKG_ROOT}"
    export VCPKG_ROOT
else
    stub_vcpkg.sh
fi

cmake -G "Ninja Multi-Config" \
    -DCMAKE_BUILD_TYPE=Release \
    -DUSE_ZIG=OFF \
    -DBUNDLE_PYSHP=OFF \
    -B build_linux \
    -S .

cmake --build build_linux --parallel $(nproc)