"""Ed25519 signature verification in pure Python (RFC 8032 §5.1.7).

Why this file exists: the reference implementation promises **zero
dependencies**, and Ed25519 is not in the Python standard library. Pulling in
PyNaCl or `cryptography` to verify one signature would break that promise for
every downstream user. Verification is not secret-dependent, so a
straightforward implementation is appropriate here.

⚠️  VERIFICATION ONLY. There is no signing function, and there should not be
    one: this code makes no attempt at constant-time arithmetic, so using it
    with a private key would leak that key through timing. Signers must use a
    vetted library.

Validated against the three official RFC 8032 §7.1 test vectors, plus negative
cases (flipped signature bit, altered message, all-zero signature).
"""
import hashlib

P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, P - 2, P) % P
I = pow(2, (P - 1) // 4, P)


def _recover_x(y: int, sign: int):
    if y >= P:
        return None
    x2 = (y * y - 1) * pow(D * y * y + 1, P - 2, P) % P
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P != 0:
        x = x * I % P
    if (x * x - x2) % P != 0:
        return None
    if x & 1 != sign:
        x = P - x
    return x


# Points in extended homogeneous coordinates (X, Y, Z, T): x = X/Z, y = Y/Z.
_GY = 4 * pow(5, P - 2, P) % P
_GX = _recover_x(_GY, 0)
G = (_GX, _GY, 1, _GX * _GY % P)


def _add(p, q):
    a = (p[1] - p[0]) * (q[1] - q[0]) % P
    b = (p[1] + p[0]) * (q[1] + q[0]) % P
    c = 2 * p[3] * q[3] * D % P
    d = 2 * p[2] * q[2] % P
    e, f, g, h = b - a, d - c, d + c, b + a
    return (e * f % P, g * h % P, f * g % P, e * h % P)


def _mul(s: int, p):
    q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            q = _add(q, p)
        p = _add(p, p)
        s >>= 1
    return q


def _equal(p, q) -> bool:
    return (p[0] * q[2] - q[0] * p[2]) % P == 0 and (p[1] * q[2] - q[1] * p[2]) % P == 0


def _decompress(b: bytes):
    if len(b) != 32:
        return None
    y = int.from_bytes(b, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    return None if x is None else (x, y, 1, x * y % P)


def verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """True if `signature` is a valid Ed25519 signature of `message`.

    Never raises on malformed input — a bad key, a bad signature and a forged
    signature are all simply False.
    """
    if len(public_key) != 32 or len(signature) != 64:
        return False
    a = _decompress(public_key)
    if a is None:
        return False
    r_bytes = signature[:32]
    r = _decompress(r_bytes)
    if r is None:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= L:                      # rejects malleable / out-of-range scalars
        return False
    k = int.from_bytes(hashlib.sha512(r_bytes + public_key + message).digest(), "little") % L
    return _equal(_mul(s, G), _add(r, _mul(k, a)))
