# ============================================================
# 2. 32-BIT HASH FUNCTION
# ============================================================

from math import log2

from lession_03.lab_hashing.lab02 import MASK
from lession_03.lab_hashing.lab05_correction_ava import rotate_left


def hash32(data: bytes) -> int:
    h = 0x811C9DC5

    for byte in data:
        h ^= byte
        h = (h * 0x01000193) & MASK
        h = rotate_left(h, 5)
        h ^= h >> 13
        h = (h * 0x85EBCA6B) & MASK

    return h & MASK


# ============================================================
# MERKLE TREE NODE
# ============================================================

class TreeMerkleNode:

    def __init__(self, data=None, node_gauche=None, node_droite=None):

        self.data = hash32(data) if data is not None else None

        self.node_gauche = node_gauche
        self.node_droite = node_droite


# ============================================================
# TRANSACTIONS
# ============================================================

transaction = [
    b"Transaction A: Amine sends 10 TND",
    b"Transaction B: Ali sends 20 TND",
    b"Transaction C: Sara sends 30 TND",
    b"Transaction D: Mohamed sends 40 TND"
]


# ============================================================
# MERKLE TREE
# ============================================================

class TreeMerlede:

    def __init__(self):

        self.transaction = transaction.copy()

        self.root = TreeMerkleNode()

        self.parents = []
        self.leaves = []


    # ========================================================
    # BUILD EMPTY MERKLE TREE
    # ========================================================

    def build_tree_vide(self, n):

        if n <= 0:
            raise ValueError("The number of leaves must be positive")

        # If n is odd, add one leaf
        if n % 2 == 1:
            n += 1

        # ----------------------------------------------------
        # Create the leaves
        # ----------------------------------------------------

        self.leaves = []

        for i in range(n):
            node = TreeMerkleNode()
            self.leaves.append(node)

        current_level = self.leaves

        self.parents = []

        # ----------------------------------------------------
        # Build the tree from bottom to top
        # ----------------------------------------------------

        while len(current_level) > 1:

            parents = []

            for i in range(0, len(current_level), 2):

                parent = TreeMerkleNode(
                    node_gauche=current_level[i],
                    node_droite=current_level[i + 1]
                )

                parents.append(parent)

            self.parents.extend(parents)

            current_level = parents

        # ----------------------------------------------------
        # Root
        # ----------------------------------------------------

        self.root = current_level[0]

        return self.root, self.parents, self.leaves


    # ========================================================
    # FILL MERKLE TREE
    # ========================================================

    def fill_tree(self):

        if len(self.transaction) == 0:
            raise ValueError("No transactions available")

        # ----------------------------------------------------
        # Duplicate last transaction if number is odd
        # ----------------------------------------------------

        if len(self.transaction) % 2 == 1:
            self.transaction.append(self.transaction[-1])

        # ----------------------------------------------------
        # Build empty tree
        # ----------------------------------------------------

        self.build_tree_vide(len(self.transaction))

        # ----------------------------------------------------
        # Fill leaves with transaction hashes
        # ----------------------------------------------------

        for i in range(len(self.transaction)):

            self.leaves[i].data = hash32(self.transaction[i])

        # ----------------------------------------------------
        # Calculate hashes of internal nodes
        # ----------------------------------------------------

        def calculate_hash(node):

            if node.node_gauche is None and node.node_droite is None:
                return node.data

            left_hash = calculate_hash(node.node_gauche)
            right_hash = calculate_hash(node.node_droite)

            # Convert the two 32-bit hashes to bytes
            combined = (
                left_hash.to_bytes(4, byteorder="big") +
                right_hash.to_bytes(4, byteorder="big")
            )

            node.data = hash32(combined)

            return node.data

        # ----------------------------------------------------
        # Calculate Merkle root
        # ----------------------------------------------------

        calculate_hash(self.root)

        return self.root.data


    # ========================================================
    # DISPLAY TREE
    # ========================================================

    def display_tree(self, node=None, level=0, prefix="Root:"):

        if node is None:
            node = self.root

        print(" " * (level * 4) + prefix + f" {node.data}")

        if node.node_gauche is not None:
            self.display_tree(
                node.node_gauche,
                level + 1,
                "Left:"
            )

        if node.node_droite is not None:
            self.display_tree(
                node.node_droite,
                level + 1,
                "Right:"
            )



def hash_pair(left, right):
    data = (
        left.to_bytes(4, "big") +
        right.to_bytes(4, "big")
    )
    return hash32(data)


def generate_proof(transactions, index):
    level = [hash32(tx) for tx in transactions]
    proof = []

    while len(level) > 1:

        # If odd number of nodes, duplicate last
        if len(level) % 2 != 0:
            level.append(level[-1])

        sibling_index = index ^ 1
        sibling_hash = level[sibling_index]

        sibling_is_left = sibling_index < index

        proof.append((sibling_hash, sibling_is_left))

        # Build next level
        next_level = []

        for i in range(0, len(level), 2):
            parent = hash_pair(level[i], level[i + 1])
            next_level.append(parent)

        level = next_level
        index //= 2

    return proof


def verify_proof(transaction, proof, trusted_root):
    current_hash = hash32(transaction)

    for sibling_hash, sibling_is_left in proof:

        if sibling_is_left:
            current_hash = hash_pair(
                sibling_hash,
                current_hash
            )
        else:
            current_hash = hash_pair(
                current_hash,
                sibling_hash
            )

    return current_hash == trusted_root
# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    tree = TreeMerlede()

    merkle_root = tree.fill_tree()

    print("\n========== MERKLE TREE ==========")

    tree.display_tree()

    # Save trusted root
    trusted_root = tree.root.data

    # Generate proof for C (index 2)
    proof = generate_proof(transaction, 2)

    # Verify C
    result = verify_proof(
     b"Transaction C: Sara sends 30 TND",
        proof,
        trusted_root
    )

    print("\n========== PROOF VERIFICATION ==========")
    print(f"Transaction C is valid ?: {result}")

    print("\n========== MERKLE ROOT ==========")

    print(f"0x{merkle_root:08X}")