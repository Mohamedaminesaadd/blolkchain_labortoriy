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

    return h


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
    b"transaction for A",
    b"transaction for B",
    b"transaction for C",
    b"transaction for D",
    b"transaction for E",
    b"transaction for F",
    b"transaction for G",
]


# ============================================================
# MERKLE TREE
# ============================================================

class TreeMerlede:

    def __init__(self):

        self.transaction = transaction

        self.root = TreeMerkleNode()

        self.node_gauche = None
        self.node_droite = None


    # ========================================================
    # BUILD EMPTY MERKLE TREE
    # ========================================================

    def build_tree_vide(self, n):

        # If the number of transactions is odd,
        # add one leaf
        if n % 2 == 1:
            n = n + 1


        # ----------------------------------------------------
        # Create the leaves
        # ----------------------------------------------------

        leaves = []

        for i in range(n):

            node = TreeMerkleNode()

            leaves.append(node)


        # ----------------------------------------------------
        # Build the tree from bottom to top
        # ----------------------------------------------------

        while len(leaves) > 1:

            parents = []

            for i in range(0, len(leaves), 2):

                parent = TreeMerkleNode(
                    node_gauche=leaves[i],
                    node_droite=leaves[i + 1]
                )

                parents.append(parent)

            leaves = parents


        # ----------------------------------------------------
        # The last remaining node is the root
        # ----------------------------------------------------

        self.root = leaves[0]


    # ========================================================
    # FILL MERKLE TREE
    # ========================================================
