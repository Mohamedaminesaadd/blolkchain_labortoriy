# RSA — du modèle pédagogique à RSA-4096 réel

> Guide en deux parties : **(A)** comprendre RSA avec de petits nombres, **(B)** l'utiliser correctement en pratique.

## Sommaire

- [Partie A — RSA pédagogique](#partie-a--rsa-pédagogique)
  - [1. Exemple chiffré](#1-exemple-chiffré)
  - [2. Algorithme complet](#2-algorithme-complet)
  - [3. Code Python complet](#3-code-python-complet)
  - [4. Les deux erreurs à éviter](#4-les-deux-erreurs-à-éviter)
  - [5. Exponentiation modulaire rapide](#5-exponentiation-modulaire-rapide)
- [Partie B — RSA réel](#partie-b--rsa-réel)
  - [6. Signification de RSA-2048 / 3072 / 4096](#6-signification-de-rsa-2048--3072--4096)
  - [7. Pourquoi ne pas utiliser RSA « brut »](#7-pourquoi-ne-pas-utiliser-rsa--brut-)
  - [8. Code RSA-4096 avec `cryptography`](#8-code-rsa-4096-avec-cryptography)
  - [9. Sauvegarde des clés](#9-sauvegarde-des-clés)
  - [10. Pourquoi `e = 65537`](#10-pourquoi-e--65537)
  - [11. Pourquoi OAEP](#11-pourquoi-oaep)
  - [12. Limite de taille du message](#12-limite-de-taille-du-message)
  - [13. Chiffrement hybride (HTTPS)](#13-chiffrement-hybride-https)
  - [14. Signatures RSA-PSS](#14-signatures-rsa-pss)
- [Récapitulatif](#récapitulatif)
- [Parcours d'apprentissage](#parcours-dapprentissage)

---

# Partie A — RSA pédagogique

## 1. Exemple chiffré

Paramètres :

| Symbole | Valeur | Rôle |
|:-------:|:------:|------|
| $p$ | 5 | premier secret |
| $q$ | 11 | premier secret |
| $n = p \times q$ | 55 | modulus (public) |
| $\varphi(n) = (p-1)(q-1)$ | 40 | secret |
| $e$ | 3 | exposant public |
| $m$ | 7 | message |

### Chiffrement

$$
c = m^e \bmod n = 7^3 \bmod 55 = 343 \bmod 55 = 13
$$

$$
\boxed{c = 13}
$$

### Calcul de la clé privée $d$

$d$ doit vérifier :

$$
e \times d \equiv 1 \pmod{\varphi(n)}
$$

Soit :

$$
3d \equiv 1 \pmod{40} \;\Rightarrow\; d = 27
$$

car $3 \times 27 = 81 = 2 \times 40 + 1 \equiv 1 \pmod{40}$.

$$
\boxed{d = 27}
$$

### Déchiffrement

$$
m = c^d \bmod n = 13^{27} \bmod 55 = 7
$$

$$
\boxed{m = 7}
$$

### Clés obtenues

| Clé | Valeur |
|-----|--------|
| **Publique** $(e, n)$ | $(3,\ 55)$ |
| **Privée** $(d, n)$ | $(27,\ 55)$ |

---

## 2. Algorithme complet

```text
                 GÉNÉRATION DES CLÉS
                         │
                ┌────────┴────────┐
                │                 │
           générer p         générer q
                │                 │
                └────────┬────────┘
                         │
                      n = p × q
                         │
                φ(n) = (p-1)(q-1)
                         │
                         ↓
                      choisir e
                         │
                         ↓
                  calculer d = e⁻¹ mod φ(n)
                         │
              ┌──────────┴──────────┐
              ↓                     ↓
         CLÉ PUBLIQUE          CLÉ PRIVÉE
            (e, n)                (d, n)
```

```text
   MESSAGE m
       │
       ↓   m^e mod n        (clé publique)
   CHIFFRÉ c
       │
       ↓   c^d mod n        (clé privée)
   MESSAGE m
```

---

## 3. Code Python complet

```python
from math import gcd


def mod_pow(base, exponent, modulus):
    """Exponentiation modulaire rapide : base^exponent mod modulus."""
    result = 1
    base %= modulus

    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent //= 2

    return result


# --- Génération des clés ---
p, q = 5, 11
n = p * q
phi = (p - 1) * (q - 1)
e = 3

assert gcd(e, phi) == 1, "e doit être premier avec phi(n)"

# d tel que e*d ≡ 1 (mod phi)
d = next(k for k in range(2, phi) if (e * k) % phi == 1)
# Équivalent en Python 3.8+ : d = pow(e, -1, phi)

# --- Chiffrement / déchiffrement ---
m = 7
c = mod_pow(m, e, n)    # chiffrement  : m^e mod n
m1 = mod_pow(c, d, n)   # déchiffrement : c^d mod n  (modulo n !)

print(f"n = {n}")
print(f"phi = {phi}")
print(f"e = {e}")
print(f"Original message = {m}")
print(f"Encrypted message = {c}")
print(f"Private exponent d = {d}")
print(f"Decrypted message = {m1}")
```

Sortie :

```text
n = 55
phi = 40
e = 3
Original message = 7
Encrypted message = 13
Private exponent d = 27
Decrypted message = 7
```

---

## 4. Les deux erreurs à éviter

### Erreur n°1 — mauvaise définition de $d$

$$
e \times d \equiv 1 \pmod{\varphi(n)}
$$

### Erreur n°2 — déchiffrer modulo $\varphi(n)$ au lieu de $n$

```python
# ❌ Faux
m1 = (c ** d) % ((p - 1) * (q - 1))

# ✅ Correct
m1 = pow(c, d, n)
```

La formule est $m = c^d \bmod n$, **pas** modulo $\varphi(n)$.

---

## 5. Exponentiation modulaire rapide

Pour de petits nombres, `(c ** d) % n` fonctionne. Mais RSA utilise de très grands nombres :

```python
m = 123456789
e = 65537
c = (m ** e) % n   # crée d'abord un entier gigantesque
```

On calcule donc $m^e \bmod n$ par **exponentiation rapide** (square-and-multiply) : on réduit modulo $n$ à chaque étape, ce qui garde les nombres petits.

### Exemple : $3^{13} \bmod 55$

$13 = 1101_2$. On parcourt les bits de droite à gauche :

| exposant | bit | base | résultat |
|:--------:|:---:|:----:|:--------:|
| 13 | 1 | 3  | $1 \times 3 = 3$ |
| 6  | 0 | 9  | 3 |
| 3  | 1 | 26 | $3 \times 26 = 78 \equiv 23$ |
| 1  | 1 | 16 | $23 \times 16 = 368 \equiv 38$ |

À chaque tour : `base = base² mod 55` ($3 \to 9 \to 81 \equiv 26 \to 676 \equiv 16$).

$$
3^{13} \bmod 55 = 38
$$

En Python, `pow(base, exp, mod)` fait exactement cela nativement.

---

# Partie B — RSA réel

## 6. Signification de RSA-2048 / 3072 / 4096

Le nombre désigne la **taille du modulus $n$ en bits** :

$$
n = p \times q
$$

| Type | Taille de $n$ | Statut |
|------|--------------:|--------|
| RSA-1024 | 1024 bits | ❌ obsolète |
| RSA-2048 | 2048 bits | ✅ standard courant |
| RSA-3072 | 3072 bits | ✅ sécurité plus élevée |
| RSA-4096 | 4096 bits | ✅ très robuste, plus lent |

> **RSA-4096 ne signifie pas que $p$ et $q$ font chacun 4096 bits.** Ils font environ la moitié (≈ 2048 bits chacun), pour que $|n| \approx 4096$ bits.

---

## 7. Pourquoi ne pas utiliser RSA « brut »

Un RSA réel n'applique jamais `pow(m, e, n)` directement sur un texte. On ajoute un **padding** :

**Chiffrement**

```text
Message → padding OAEP → RSA → Ciphertext
```

**Signature**

```text
Message → Hash (SHA-256 / SHA-384 / …) → RSA-PSS → Signature
```

---

## 8. Code RSA-4096 avec `cryptography`

Pour du RSA réel, utiliser une bibliothèque éprouvée plutôt que de réimplémenter RSA.

```bash
pip install cryptography
```

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes


# 1. Génération de la paire de clés RSA-4096
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
)
public_key = private_key.public_key()

# 2. Message
message = b"Hello, this is a secret message."

# 3. Chiffrement avec la clé publique (OAEP + SHA-256)
oaep = padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None,
)

ciphertext = public_key.encrypt(message, oaep)
print("Ciphertext:")
print(ciphertext.hex())

# 4. Déchiffrement avec la clé privée
plaintext = private_key.decrypt(ciphertext, oaep)
print("\nDecrypted message:")
print(plaintext.decode())
```

```text
                 RSA-4096
              ┌─────────────┐
              │             │
         Clé publique   Clé privée
          (e, n)          (d, n)
              │             │
              ↓             ↓
          CHIFFRER      DÉCHIFFRER
```

---

## 9. Sauvegarde des clés

En pratique, les clés ne restent pas seulement en RAM.

```python
from cryptography.hazmat.primitives import serialization

# Clé privée (PKCS#8, PEM)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
with open("private_key.pem", "wb") as f:
    f.write(private_pem)

# Clé publique (SubjectPublicKeyInfo, PEM)
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
with open("public_key.pem", "wb") as f:
    f.write(public_pem)
```

```text
rsa/
├── private_key.pem    ← SECRÈTE
└── public_key.pem     ← distribuable
```

> ⚠️ `NoEncryption()` écrit la clé privée en clair sur disque : acceptable pour un TP, pas pour un vrai projet. Utiliser alors `serialization.BestAvailableEncryption(b"mot-de-passe")` et restreindre les permissions du fichier.

---

## 10. Pourquoi `e = 65537`

Dans l'exemple pédagogique, $e = 3$ suffit pour comprendre. Les implémentations modernes utilisent :

$$
\boxed{e = 65537 = 2^{16} + 1}
$$

C'est un choix très répandu : il permet une exponentiation efficace (seulement deux bits à 1 en binaire) tout en évitant les problèmes liés aux très petits exposants.

---

## 11. Pourquoi OAEP

RSA « brut » est **déterministe** :

$$
c = m^e \bmod n
$$

```text
HELLO → ciphertext A
HELLO → ciphertext A     ← identique : mauvais pour un vrai système
```

Avec **RSA-OAEP**, un aléa est injecté à chaque chiffrement :

```text
HELLO → OAEP + aléa 1 → RSA → ciphertext A
HELLO → OAEP + aléa 2 → RSA → ciphertext B     ← différent
```

---

## 12. Limite de taille du message

RSA n'est **pas conçu pour chiffrer de gros fichiers**. Avec RSA-OAEP, la taille maximale du message est :

$$
k - 2 \cdot hLen - 2
$$

où $k$ est la taille du modulus en octets et $hLen$ la taille du hash.

Pour RSA-4096 avec SHA-256 :

$$
k = \frac{4096}{8} = 512, \qquad hLen = 32
$$

$$
512 - 2 \times 32 - 2 = 446
$$

$$
\boxed{446 \text{ octets maximum}}
$$

---

## 13. Chiffrement hybride (HTTPS)

Pour un gros fichier, on combine deux algorithmes :

```text
        MESSAGE / FICHIER
               │
               ↓
         AES-256-GCM  ◄──── clé AES
               │                │
               ↓                ↓
        données chiffrées   RSA-OAEP
                                │
                                ↓
                       clé AES chiffrée
```

- **AES** chiffre les données (rapide).
- **RSA** protège la clé AES (petite, donc compatible avec la limite de 446 octets).

---

## 14. Signatures RSA-PSS

RSA sert aussi à signer :

```text
        Document
            │
            ↓
         SHA-256
            │
            ↓
     RSA-PSS (clé privée)
            │
            ↓
        Signature
```

Le destinataire vérifie avec la **clé publique** :

```text
Document + Signature + Clé publique  →  VALIDE ?
```

Propriétés assurées : authenticité, intégrité, et non-répudiation dans les systèmes appropriés.

---

# Récapitulatif

| RSA pédagogique | RSA réel |
|-----------------|----------|
| petits $p, q$ | grands nombres premiers |
| `e = 3` | généralement `e = 65537` |
| `pow(m, e, n)` | RSA + padding |
| pas de padding | OAEP (chiffrement) / PSS (signature) |
| message = un entier | octets + protocole |
| RSA sur le message | RSA généralement hybride |
| pas de protection des clés | PEM / PKCS#8, stockage sécurisé |
| boucle pour trouver $d$ | algorithmes efficaces (Euclide étendu) |
| RSA seul | RSA + AES + SHA-256 |

> **Point essentiel :** `RSA-4096` indique la **taille du modulus** ; `OAEP` / `PSS` indiquent **comment RSA est utilisé de façon sûre**. Ce sont deux notions distinctes.

---

# Parcours d'apprentissage

```text
RSA mathématique
      ↓
RSA from scratch
      ↓
Algorithme d'Euclide étendu
      ↓
Exponentiation modulaire rapide
      ↓
Génération de nombres premiers
      ↓
RSA-2048 / RSA-4096
      ↓
OAEP
      ↓
RSA-PSS
      ↓
Chiffrement hybride
      ↓
AES-256-GCM + RSA-OAEP
      ↓
Signatures numériques
      ↓
TLS / HTTPS
```