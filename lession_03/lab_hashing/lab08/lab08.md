Excellent! You have implemented the core of your Hash-Based File Integrity Checker using Python's `hashlib`, `json`, and `pathlib`.

Your implementation is already functional. Let's analyze it as a cybersecurity lab and identify what you should implement next.

## 1. What your code currently does

Your program has two main operations:

### `init` — Create the baseline

```
python verify.py init
```

For every file:

1. Check whether the file exists.
2. Read its content in binary mode.
3. Calculate its SHA-256 hash.
4. Store the hash in `manifest.json`.

Example:

```
{
    "app.py": "a8f5f167f44f4964e6c998dee827110c...",
    "config.json": "b3a1f5c7..."
}
```

This manifest represents the original state of your files.

### `verify` — Detect modifications

```
python verify.py verify
```

Your program recalculates each file's hash and compares it with the expected hash.

| Situation      | Result       |
| -------------- | ------------ |
| File unchanged | `[OK]`       |
| File modified  | `[MODIFIED]` |
| File deleted   | `[MISSING]`  |

## 2. Let's test your implementation

Create a test environment:

```
project/
├── app.py
├── config.json
├── database.py
├── README.md
└── verify.py
```

### Test 1 — Normal verification

```
python verify.py init
python verify.py verify
```

Expected:

```
[OK] app.py
[OK] config.json
[OK] database.py
[OK] README.md
```

### Test 2 — Detect a modification

Open `app.py` and add:

```
print("Hello Cybersecurity")
```

Then:

```
python verify.py verify
```

Expected:

```
[MODIFIED] app.py
[OK] config.json
[OK] database.py
[OK] README.md
```

### Test 3 — Detect deletion

Delete `database.py`.

Run verification again.

Expected:

```
[MISSING] database.py
```

## 3. Important security limitation

Your implementation detects modifications, but it does not yet protect the manifest itself.

Imagine an attacker changes:

```
app.py
```

and then executes:

```
python verify.py init
```

The new malicious file hash becomes the trusted baseline.

This is called a trust-anchor problem.

For a more secure design, the manifest should be protected using mechanisms such as:

- HMAC-SHA256 with a secret key.
- Digital signatures using RSA or Ed25519.
- A read-only or separately protected manifest.

We will implement these progressively.

## 4. Your next lab: Improve the integrity checker

I recommend following this roadmap:

## Hash-Based File Integrity Project

1. Lab 01 — SHA-256 File Hashing

   Completed

   Calculate hashes using `hashlib`.
2. Lab 02 — Manifest Creation and Verification

   Implemented

   Generate and verify `manifest.json`.
3. Lab 03 — Robust Verification

   Next
   - Detect missing files.
   - Detect unexpected files.
   - Validate manifest structure.
   - Return appropriate exit codes.
   - Handle corrupted JSON.
4. Lab 04 — HMAC-SHA256

   Authenticate the manifest using a secret key.
5. Lab 05 — Merkle Tree

   Build a tree of hashes and calculate its root hash.
6. Lab 06 — Digital Signatures

   Sign the manifest with a private key and verify it using a public key.
7. Lab 07 — Real-Time Integrity Monitoring

   Detect file changes automatically using Python's `watchdog`.

## My recommendation

Before moving to HMAC, let's improve your current code by implementing Lab 03: Robust Verification.

The objective is to make your program behave like a real integrity-monitoring utility, with a clear distinction between:

```
[OK]        File is intact
[MODIFIED]  File content changed
[MISSING]   Expected file does not exist
[UNEXPECTED] New file detected
[ERROR]     Manifest is invalid
```

This will also introduce you to an important cybersecurity principle: integrity verification must detect both unauthorized modifications and changes to the set of monitored files.



# Hash-Based File Integrity (HBFI)

Hash-Based File Integrity is a security mechanism that verifies whether a file has been modified, corrupted, or replaced by comparing its current cryptographic hash with a previously recorded hash.

It is widely used in operating system security, malware detection, digital forensics, software verification, and backup systems.

Let's understand how it works internally and why it is useful.

## 1. First, understand the basic idea

Imagine that a Linux server contains a critical configuration file:

```
/etc/ssh/sshd_config
```

This file controls SSH server configuration.

An administrator wants to know whether someone has modified it without authorization.

The administrator calculates its SHA-256 hash.

For example:

```
File: sshd_config

SHA256:
A1B2C3D4E5F6...
```

This hash represents the content of the file.

Later, the system calculates the hash again.

There are two possibilities:

- Same hash → The file content is unchanged.
- Different hash → The file content has changed.

This is the fundamental principle of Hash-Based File Integrity.

## 2. How does it work step by step?

A typical file integrity system has two phases.

### Phase 1: Establishing a trusted baseline

Suppose a system contains three files:

```
server/
├── app.py
├── config.json
└── database.py
```

When the administrator trusts the current state of these files, the system calculates their hashes.

For example:

| File        | SHA-256   |
| ----------- | --------- |
| app.py      | `A91F...` |
| config.json | `B82D...` |
| database.py | `C73E...` |

These hashes are saved in a file called a manifest.

```
manifest.json
```

The manifest acts as a reference for future verification.

Conceptually:

```
Original files
      |
      v
SHA-256 algorithm
      |
      v
Calculate hashes
      |
      v
Save trusted hashes
      |
      v
manifest.json
```

### Phase 2: Verification

After some time, the system scans the files again.

It calculates new hashes and compares them with the original values.

Example:

| File        | Original hash | Current hash | Result    |
| ----------- | ------------- | ------------ | --------- |
| app.py      | `A91F...`     | `A91F...`    | Unchanged |
| config.json | `B82D...`     | `X91A...`    | Modified  |
| database.py | `C73E...`     | `C73E...`    | Unchanged |

The system detects that `config.json` has changed.

The important point is that the system does not need to understand the contents of the file. It only compares the cryptographic fingerprints.

## 3. Why does a small modification change the hash?

This is related to a cryptographic property called the Avalanche Effect.

Consider two files:

Original:

```
Hello World
```

Modified:

```
Hello world
```

Only one character has changed: `W` became `w`.

However, their SHA-256 hashes will be completely different.

For illustration:

```
SHA256("Hello World")
= a591a6d40bf420404a011733...

SHA256("Hello world")
= 64ec88ca00b268e5ba1a3567...
```

SHA-256 always produces a 256-bit digest, represented by 64 hexadecimal characters.

A small change in the input causes a large, unpredictable change in the output.

This makes cryptographic hashes useful for detecting file modifications.

## 4. Where is Hash-Based File Integrity used?

### A. Operating System Security

Operating systems contain important files that should not be modified unexpectedly.

Examples on Linux:

```
/etc/passwd
/etc/shadow
/etc/ssh/sshd_config
/usr/bin/
```

A malicious user or malware might modify a system executable or configuration file.

A File Integrity Monitoring (FIM) system periodically checks these files.

Example:

```
[OK] /etc/passwd
[OK] /etc/ssh/sshd_config
[ALERT] /usr/bin/important_app
```

The alert indicates that the file's content differs from its trusted baseline.

Tools that provide file integrity monitoring include:

- AIDE
- Tripwire
- Wazuh

### B. Malware and Intrusion Detection

Imagine an attacker compromises a server and replaces a legitimate executable with a modified version.

```
Before attack:

/usr/bin/application
SHA256 = ABC123

After attack:

/usr/bin/application
SHA256 = XYZ789
```

The integrity monitoring system detects the difference.

This helps security administrators investigate:

- Unauthorized executable modifications
- Changes to startup scripts
- Alterations to system configuration
- Unexpected changes to critical application files

Note that a changed hash indicates modification, not necessarily malware.

### C. Software Download Verification

When downloading software, a vendor may publish the expected SHA-256 checksum.

For example:

```
Downloaded file:
ubuntu.iso

Published SHA256:
ABC123...

Calculated SHA256:
ABC123...
```

If both match, the downloaded file has the same content as the file represented by the published digest.

This is useful for detecting accidental corruption or unexpected modifications during distribution.

However, if an attacker can replace both the download and its checksum, a hash comparison alone cannot establish authenticity. A trusted digital signature provides stronger authentication.

### D. Digital Forensics

In digital forensics, investigators need to preserve the integrity of digital evidence.

Imagine an investigator creates a copy of a hard disk.

```
Original evidence:
disk_image.dd

SHA256:
A1B2C3...
```

After copying:

```
Copied evidence:
disk_copy.dd

SHA256:
A1B2C3...
```

Matching hashes support the conclusion that the copy is identical to the original at the time of hashing.

This is important for documenting evidence handling and detecting accidental changes.

### E. Backup and Storage Systems

Hashing is also used to detect corruption in stored data.

For example:

```
backup_2026.tar
```

A system can calculate a checksum when the backup is created and verify it later.

If the checksum differs, the data may have been corrupted or modified.

This is useful in:

- Database backups
- Cloud storage
- Archival systems
- File transfer
- Distributed storage

## 5. What happens if an attacker modifies both the file and manifest?

This is an important security limitation.

Suppose the original state is:

```
config.json  → HASH_A
manifest.json → HASH_A
```

An attacker changes the configuration file and also updates the manifest:

```
config.json  → HASH_B
manifest.json → HASH_B
```

The verification system compares the two values:

```
HASH_B == HASH_B
```

It reports that the file is unchanged relative to the manifest, even though the file was modified.

Therefore, the manifest itself must be protected.

Possible solutions include:

| Technique              | Purpose                                           |
| ---------------------- | ------------------------------------------------- |
| Restricted permissions | Prevent unauthorized manifest modification        |
| Remote storage         | Keep trusted hashes outside the monitored machine |
| HMAC                   | Authenticate the manifest using a secret key      |
| Digital signature      | Verify the manifest using a public key            |

This illustrates a fundamental principle of security: you must protect the trusted reference used to verify integrity.

## 6. Difference between hashing, integrity monitoring, and digital signatures

These concepts are related but not identical.

| Concept                   | What it does                                                                    |
| ------------------------- | ------------------------------------------------------------------------------- |
| Cryptographic hashing     | Calculates a digest from data                                                   |
| File Integrity Monitoring | Uses hashes to detect file changes                                              |
| HMAC                      | Provides integrity and authentication using a shared secret                     |
| Digital signature         | Allows verification of integrity and authenticity using public-key cryptography |

For example, SHA-256 alone does not tell you who created a file or whether its author is trustworthy.

It only provides a fingerprint of its content.

## 7. The complete concept in one diagram

```
             INITIAL STATE
                   |
                   v
             Trusted Files
                   |
                   v
              SHA-256
                   |
                   v
           Original Hashes
                   |
                   v
             Manifest.json
                   |
                   |
             Time passes
                   |
                   v
          Current File System
                   |
                   v
              SHA-256
                   |
                   v
            Current Hashes
                   |
                   v
         Compare with Manifest
                   |
           +-------+-------+
           |               |
        Equal           Different
           |               |
           v               v
      No content       Modification
        change          detected
           |               |
           v               v
      Integrity OK       Alert
```

In one sentence: Hash-Based File Integrity uses cryptographic fingerprints to establish a trusted reference for files and detect when their contents change over time.