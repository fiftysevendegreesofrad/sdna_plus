#!/usr/bin/env bash
set -euo pipefail

# build_linux.sh — Single-command Linux build for sDNA+
# Produces output/Release/x64/sdna_vs2008.so with OpenMP support
#
# Usage:
#   bash build_linux.sh
#
# Install the prerequisites first (this is the only step that needs root).
# On Debian based distros (e.g. Ubuntu):
#   sudo apt install cmake make g++ libboost-dev python3
#
# Note: CMake 3.29 is required.
# Some older distro CMake packages are too old; install a newer CMake from
# Kitware's apt repo or pip (pip install cmake) if the configure step fails.
# E.g. https://apt.kitware.com/

SCRIPT_DIR="$(dirname $0)"
BUILD_DIR="${SCRIPT_DIR}/build_linux"
OUTPUT_DIR="${SCRIPT_DIR}/output/Release/x64"
STUB_VCPKG_ROOT="/tmp/sdna_vcpkg_stub"

echo "========================================"
echo " sDNA+ Linux Build (with OpenMP)"
echo "========================================"
echo ""

# ---- Check prerequisites ----
MISSING=""
for cmd in cmake g++ make; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "  MISSING: $cmd"
        MISSING="$MISSING $cmd"
    fi
done

if [ -n "$MISSING" ]; then
    echo ""
    echo "ERROR: Required tools not found:$MISSING"
    echo "Install them first (needs root), e.g. on Ubuntu/Debian:"
    echo "  sudo apt install cmake make g++ libboost-dev python3"
    exit 1
fi

# Check for Boost headers
if [ ! -d /usr/include/boost ]; then
    echo "ERROR: Boost headers not found at /usr/include/boost"
    echo "Install with: sudo apt install libboost-dev"
    exit 1
fi

echo "Prerequisites OK (cmake, g++, make, boost)"
echo ""

# ---- Set up vcpkg toolchain stub ----
# The project CMake requires a vcpkg toolchain file.
# If VCPKG_ROOT is set and contains a real vcpkg, use it (pins Boost 1.83).
# Otherwise, create a stub that uses system packages.
if [ -n "${VCPKG_ROOT:-}" ] && [ -f "${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" ]; then
    echo "Using vcpkg from VCPKG_ROOT=${VCPKG_ROOT}"
    export VCPKG_ROOT
else
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
fi

# ---- Clean previous build ----
rm -rf "${BUILD_DIR}"

# ---- Configure ----
echo ""
echo "=== Configuring (Unix Makefiles, Release) ==="
cmake -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release \
    -DUSE_ZIG=OFF \
    -DBUNDLE_PYSHP=OFF \
    -DCMAKE_MAKE_PROGRAM="$(command -v make)" \
    -B "${BUILD_DIR}" \
    -S "${SCRIPT_DIR}"

# ---- Build ----
echo ""
echo "=== Building (parallel: $(nproc) jobs) ==="
cmake --build "${BUILD_DIR}" --parallel "$(nproc)" 2>&1 || {
    # The .so may have built but post-build copy failed (Unix Makefiles
    # path mismatch with CMAKE_CONFIGURATION_TYPES override). Check.
    if [ -f "${BUILD_DIR}/sDNA/sdna_vs2008/sdna_vs2008.so" ]; then
        echo ""
        echo "NOTE: .so built but post-build copy failed (expected with Unix Makefiles generator)."
        echo "      Assembling output by hand..."
    else
        echo ""
        echo "BUILD FAILED — see errors above"
        exit 1
    fi
}

# ---- Assemble output directory ----
echo ""
echo "=== Assembling output/Release/x64/ ==="
mkdir -p "${OUTPUT_DIR}"

# Copy the sDNA shared library
SO_SRC="${BUILD_DIR}/sDNA/sdna_vs2008/sdna_vs2008.so"
if [ -f "${SO_SRC}" ]; then
    cp -v "${SO_SRC}" "${OUTPUT_DIR}/"
else
    echo "ERROR: sdna_vs2008.so not found at ${SO_SRC}"
    exit 1
fi

# Copy geos shared library (pre-built, in-tree)
GEOS_SRC="${SCRIPT_DIR}/sDNA/geos/x64/src/libgeos_c.so"
if [ -f "${GEOS_SRC}" ]; then
    cp -v "${GEOS_SRC}" "${OUTPUT_DIR}/"
else
    echo "WARNING: libgeos_c.so not found at ${GEOS_SRC} — geos functions may fail"
fi

# Copy Python scripts
echo "Copying Python scripts..."
rsync -a --exclude='__pycache__' "${SCRIPT_DIR}/arcscripts/" "${SCRIPT_DIR}/output/Release/" 2>/dev/null || \
    cp -r "${SCRIPT_DIR}/arcscripts/"* "${SCRIPT_DIR}/output/Release/" 2>/dev/null || true

# Copy bin scripts to bin subdirectory
mkdir -p "${SCRIPT_DIR}/output/Release/bin"
cp -r "${SCRIPT_DIR}/arcscripts/bin/"* "${SCRIPT_DIR}/output/Release/bin/" 2>/dev/null || true

# Copy installer bits
cp "${SCRIPT_DIR}/installerbits/license.rtf" "${SCRIPT_DIR}/output/Release/" 2>/dev/null || true

# ---- Verify ----
SO_FILE="${OUTPUT_DIR}/sdna_vs2008.so"
echo ""
echo "========================================"
if [ -f "${SO_FILE}" ]; then
    echo "BUILD SUCCESS"
    echo "Output: ${SO_FILE}"
    echo ""
    echo "File size: $(du -h "${SO_FILE}" | cut -f1)"
    echo ""

    # Check OpenMP
    echo -n "OpenMP support: "
    if readelf -d "${SO_FILE}" 2>/dev/null | grep -q 'libgomp'; then
        echo "YES — libgomp linked (multi-threaded)"
    elif nm -D "${SO_FILE}" 2>/dev/null | grep -q 'GOMP_parallel'; then
        echo "YES — GOMP symbols found (multi-threaded)"
    else
        echo "WARNING: No OpenMP detected — single-threaded build"
    fi

    # Check geos
    echo -n "GEOS support:    "
    if [ -f "${OUTPUT_DIR}/libgeos_c.so" ]; then
        echo "YES — libgeos_c.so bundled"
    else
        echo "NO — geos not bundled (spatial operations may fail)"
    fi

    echo ""
    echo "Quick test:"
    echo "  export sdnadll=\"${SO_FILE}\""
    echo "  cd sDNA/sdna_vs2008/tests"
    echo "  python3 prepare_test_new.py"
    echo ""
    echo "To run benchmarks:"
    echo "  pip install sdna-plus  # for Python bindings (or use arcscripts from output/)"

    if [ "${CI}" ] || [ "${GITHUB_ACTIONS}"]; then
        exit 0
    fi

    # ---- Offer permanent install ----
    echo ""
    echo "----------------------------------------"
    BASHRC="${HOME}/.bashrc"
    EXPORT_LINE="export sdnadll=\"${SO_FILE}\""
    PATH_LINE="export PATH=\"\${PATH}:${SCRIPT_DIR}/output/Release/bin\""

    echo "Make sDNA permanently available in new shells?"
    echo "  This will add two lines to ${BASHRC}:"
    echo "    ${EXPORT_LINE}"
    echo "    ${PATH_LINE}"
    echo ""
    read -r -p "  Update ~/.bashrc? [y/N] " REPLY
    echo ""

    if [ "${REPLY,,}" = "y" ] || [ "${REPLY,,}" = "yes" ]; then
        # Avoid duplicates
        if [ -f "${BASHRC}" ]; then
            if grep -qF "sdnadll=" "${BASHRC}" 2>/dev/null; then
                echo "sDNA entries already found in ${BASHRC} — skipping"
            else
                {
                    echo ""
                    echo "# sDNA+ (added by build_linux.sh on $(date -I))"
                    echo "${EXPORT_LINE}"
                    echo "${PATH_LINE}"
                } >> "${BASHRC}"
                echo "Added sDNA to ${BASHRC}"
                echo "Run 'source ${BASHRC}' or open a new terminal to apply."
            fi
        else
            {
                echo "# sDNA+ (added by build_linux.sh on $(date -I))"
                echo "${EXPORT_LINE}"
                echo "${PATH_LINE}"
            } > "${BASHRC}"
            echo "Created ${BASHRC} with sDNA entries"
        fi
    else
        echo "Skipped. To enable manually later:"
        echo "  echo '${EXPORT_LINE}' >> ~/.bashrc"
        echo "  echo '${PATH_LINE}' >> ~/.bashrc"
    fi
else
    echo "BUILD FAILED — ${SO_FILE} not found"
    exit 1