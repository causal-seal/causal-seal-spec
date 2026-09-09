# Test vectors — Causal Seal v1.0

## valid-001.json
Output text (UTF-8): "The sky appears blue because air molecules scatter short wavelengths of sunlight more strongly than long ones."
Expected output_hash : 63b6530c4afbe3545db2e0173e91cda673ee93001f0c597e73e9820507096bc3
Canonical form (JCS/RFC 8785): sorted member names, no whitespace, UTF-8, fingerprint/signature excluded.
Expected fingerprint : 81d931140be9a128df3091479b61aa7b496c7fc023104e57d4a5ebd4cae3740a
A conforming Level-1 verifier MUST accept this seal.

## invalid-001.json
Same seal with `identity.expert` altered to "CORP" after emission; fingerprint unchanged.
A conforming Level-1 verifier MUST reject it (recomputed fingerprint differs).

## valid-002-signed.json  (Level 2)
The same seal as `valid-001`, with an Ed25519 `signature` over its fingerprint.
Public key: `valid-002-signed.pubkey` — this is the key from **RFC 8032 §7.1
test 1**, so the signing key is public and anyone can regenerate the vector.
A conforming Level-2 verifier MUST accept it *with that key*, and MUST reject
it with any other key.

## invalid-002-forged-signature.json  (Level 2)
The same seal with a signature of **sixty-four zero bytes**.

⚠️ It passes Level 1 — it is intact. Only Level 2 exposes it. Before Level 2 was
implemented, this file verified exactly like a genuine seal, which is precisely
why the vector exists: a verifier that ignores `signature` reports authenticity
it never checked.

Signature member: `signature` = Ed25519 over the ASCII hex `fingerprint`
(SPEC §5.2), excluded from the fingerprint computation (SPEC §4).
