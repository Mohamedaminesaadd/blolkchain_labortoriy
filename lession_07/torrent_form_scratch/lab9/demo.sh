#!/usr/bin/env bash
# Runs the whole Lab 9 end to end.  Usage: ./demo.sh [path/to/lab9-binary]
set -euo pipefail
cd "$(dirname "$0")"

BIN="${1:-./build/lab9}"
mkdir -p shared pieces reconstructed

echo "=== 1. Create a 9-byte binary sample (contains 0x00 and 0xFF) ==="
printf '\x00\x01\x02\xFF\x41\x42\x43\x44\x45' > shared/example.bin
if command -v xxd >/dev/null 2>&1; then xxd shared/example.bin; else od -An -tx1 shared/example.bin; fi

echo
echo "=== 2. Split into 4-byte pieces (+ metadata.json) ==="
"$BIN" split shared/example.bin 4 pieces
echo
cat pieces/metadata.json

echo
echo "=== 3. Reconstruct from the pieces ==="
"$BIN" reconstruct pieces reconstructed

echo
echo "=== 4. Verify: cmp + SHA-256 ==="
cmp shared/example.bin reconstructed/example.bin && echo "cmp: identical (exit 0)"
"$BIN" verify shared/example.bin reconstructed/example.bin

echo
echo "=== 5. Corrupt piece 1 (first byte 0x41 -> 0x00): must be rejected ==="
printf '\x00' | dd of=pieces/piece_000001.bin bs=1 count=1 conv=notrunc 2>/dev/null
rm -f reconstructed/example.bin
if "$BIN" reconstruct pieces reconstructed; then
    echo "UNEXPECTED: corrupted piece was accepted" >&2
    exit 1
fi
test ! -e reconstructed/example.bin && test ! -e reconstructed/example.bin.part \
    && echo "(expected failure; no partial output left behind)"

echo
echo "=== 6. Delete piece 2: missing piece must be detected ==="
"$BIN" split shared/example.bin 4 pieces > /dev/null   # fresh, valid pieces
rm pieces/piece_000002.bin
if "$BIN" reconstruct pieces reconstructed; then
    echo "UNEXPECTED: missing piece was not detected" >&2
    exit 1
fi
echo "(expected failure)"

echo
echo "=== 7. Lab example: 10,500 bytes with 4,096-byte pieces ==="
head -c 10500 /dev/urandom > shared/test.bin
"$BIN" split shared/test.bin 4096 pieces
"$BIN" reconstruct pieces reconstructed > /dev/null
cmp shared/test.bin reconstructed/test.bin && echo "cmp: identical (exit 0)"
"$BIN" verify shared/test.bin reconstructed/test.bin

echo
echo "All checks passed."
