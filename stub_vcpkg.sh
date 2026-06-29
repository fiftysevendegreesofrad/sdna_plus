#!/usr/bin/env bash
set -euo pipefail

echo "No vcpkg found — using system Boost and packages"
export VCPKG_ROOT="${STUB_VCPKG_ROOT}"
mkdir -p "${VCPKG_ROOT}/scripts/buildsystems"
cat > "${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" << 'VCPKG_EOF'
# Stub vcpkg toolchain — use system packages (Boost, etc.)
if(NOT DEFINED VCPKG_TARGET_TRIPLET)
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|amd64|AMD64")
        set(VCPKG_TARGET_TRIPLET "x64-linux")
    else()
        set(VCPKG_TARGET_TRIPLET "arm64-linux")
    endif()
endif()
set(VCPKG_MANIFEST_MODE OFF)
message(STATUS "Using stub vcpkg toolchain (system packages)")
VCPKG_EOF