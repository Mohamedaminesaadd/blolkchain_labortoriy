
import hashlib
import json
from pathlib import Path

FILES = [
    "app.py",
    "config.json",
    "database.py",
    "README.md"
]

MANIFEST = "manifest.json"


def calculate_sha256(filepath):
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:
        while True:
            chunk = file.read(4096)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def create_manifest():
    manifest = {}

    for filename in FILES:
        if not Path(filename).is_file():
            print(f"[MISSING] {filename}")
            continue

        manifest[filename] = calculate_sha256(filename)

    with open(MANIFEST, "w") as file:
        json.dump(manifest, file, indent=4)

    print("[+] Manifest created successfully")


def verify_files():
    if not Path(MANIFEST).is_file():
        print("[ERROR] Manifest not found.")
        return

    with open(MANIFEST, "r") as file:
        expected_hashes = json.load(file)

    for filename, expected_hash in expected_hashes.items():

        if not Path(filename).is_file():
            print(f"[MISSING]  {filename}")
            continue

        current_hash = calculate_sha256(filename)

        if current_hash == expected_hash:
            print(f"[OK]       {filename}")
        else:
            print(f"[MODIFIED] {filename}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python verify.py [init|verify]")
    elif sys.argv[1] == "init":
        create_manifest()
    elif sys.argv[1] == "verify":
        verify_files()
    else:
        print("Unknown command")
