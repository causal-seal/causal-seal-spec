# Causal Seal — an open format for decision provenance in generative AI

> **Status: v1.0 — published for community review.** Site: [causalseal.org](https://causalseal.org) · Paper: [doi.org/10.5281/zenodo.21431267](https://doi.org/10.5281/zenodo.21431267)

Content provenance (C2PA) proves where an artifact comes from. Log integrity proves a record wasn't altered. The **Causal Seal** proves something neither does: ***why* a generative system produced a specific output** — by cryptographically binding the output to the causal parameters that governed its generation.

- **[SPEC.md](SPEC.md)** — the specification (data model, canonicalization, verification, conformance, regulatory mapping).
- **[causal_seal.py](causal_seal.py)** — minimal reference implementation, standard library only: emitter + Level-1 and Level-2 verifier + CLI (`demo`, `verify`, `selftest`). Install: `pip install causal-seal` ([PyPI](https://pypi.org/project/causal-seal/)).
- **[ed25519_pure.py](ed25519_pure.py)** — Ed25519 *verification* in pure Python (RFC 8032), so Level 2 costs no dependency. Validated against the three official RFC 8032 §7.1 vectors. Verification only: no signing function, and the arithmetic is not constant-time — signers must use a vetted library.

Level 2 in one command:

```
causal-seal verify seal.json --output-text "..." --public-key <hex|file>
```

⚠️ A seal carrying a signature that nobody checks is worse than an unsigned one — it looks like authenticity. `verify` therefore says so out loud when a `signature` is present and no key was given.
- **[causal-seal.schema.json](causal-seal.schema.json)** — JSON Schema for automated validation.
- **[test-vectors/](test-vectors/)** — computed vectors: a valid seal (with its exact expected fingerprint) and a tampered one that must fail.
- **[docs/verify.html](docs/verify.html)** — public verifier ([live](https://causalseal.org/verify.html)): paste a seal (and optionally the output text), get 🟢/🔴 — computed entirely in the browser, nothing sent anywhere. Validated against the test vectors.
- **[paper/PAPER.md](paper/PAPER.md)** — companion paper (preprint): *Causal Seals: Decision Provenance for Governed Generation* · archived preprint: [10.5281/zenodo.21431267](https://doi.org/10.5281/zenodo.21431267).
- **[pyproject.toml](pyproject.toml)** — packaging: ready for `pip install causal-seal` at publication.

```
$ python causal_seal.py selftest
OK   invalid-001.json: verifier says FAIL (fingerprint mismatch) — expected FAIL
OK   valid-001.json:   verifier says PASS (seal verified, Level 1) — expected PASS
selftest: ALL GOOD
```

The specification standardizes the **envelope of proof**, not the engine of governance: implementing the format is intended to be royalty-free (see SPEC §9); how an emitter produces a genuinely causal state is its own concern — and its own advantage.

*Spec text: CC BY 4.0. Reference implementation: zero dependencies, Python 3.10+.*
