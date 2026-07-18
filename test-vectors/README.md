# Test vectors — Causal Seal v1.0-draft

## valid-001.json
Output text (UTF-8): "The sky appears blue because air molecules scatter short wavelengths of sunlight more strongly than long ones."
Expected output_hash : 63b6530c4afbe3545db2e0173e91cda673ee93001f0c597e73e9820507096bc3
Canonical form (JCS/RFC 8785): sorted member names, no whitespace, UTF-8, fingerprint/signature excluded.
Expected fingerprint : 81d931140be9a128df3091479b61aa7b496c7fc023104e57d4a5ebd4cae3740a
A conforming Level-1 verifier MUST accept this seal.

## invalid-001.json
Same seal with `identity.expert` altered to "CORP" after emission; fingerprint unchanged.
A conforming Level-1 verifier MUST reject it (recomputed fingerprint differs).
