#!/usr/bin/env python3
"""Causal Seal v1.0-draft — minimal reference implementation (emitter + Level-1 verifier).

Standard library only. See SPEC.md.

Usage:
  python causal_seal.py demo
  python causal_seal.py verify <seal.json> [--output-text "..."] [--output-file path]
  python causal_seal.py selftest [test-vectors-dir]
"""
import json
import hashlib
import sys
import os
import datetime

SPEC_ID = "causal-seal/1.0"
REQUIRED = ("spec", "emitter", "timestamp", "output_hash", "causal_state", "dictionary", "fingerprint")
CLASSES = ("identity.", "engine.", "field.", "shaping.", "context.", "x.")


# ── Canonicalization (SPEC §4) ────────────────────────────────────────────────
# JCS (RFC 8785). For ASCII member names and string values — the only kinds a
# seal contains — canonical JSON is exactly: sorted keys, no whitespace, UTF-8.
def canonicalize(seal: dict) -> bytes:
    body = {k: v for k, v in seal.items() if k not in ("fingerprint", "signature")}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def fingerprint(seal: dict) -> str:
    return hashlib.sha256(canonicalize(seal)).hexdigest()


# ── Emitter (SPEC §3, §6) ─────────────────────────────────────────────────────
def emit_seal(emitter: str, causal_state: dict, output_text: str, dictionary: str) -> dict:
    """Build a conformant seal for one output, sealed at emission time."""
    for name, value in causal_state.items():
        if not any(name.startswith(c) for c in CLASSES):
            raise ValueError(f"parameter '{name}' is not namespaced by a defined class")
        if not isinstance(value, str):
            raise ValueError(f"parameter '{name}' must be serialized as a string (SPEC 3.2)")
    seal = {
        "spec": SPEC_ID,
        "emitter": emitter,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "output_hash": hashlib.sha256(output_text.encode("utf-8")).hexdigest(),
        "causal_state": causal_state,
        "dictionary": dictionary,
    }
    seal["fingerprint"] = fingerprint(seal)
    return seal


# ── Level-1 verifier (SPEC §5.1, §6) ─────────────────────────────────────────
def verify_seal(seal: dict, output_text: str | None = None) -> tuple[bool, str]:
    """Returns (ok, reason). Failure means 'this seal proves nothing' (SPEC 6)."""
    for member in REQUIRED:
        if member not in seal:
            return False, f"missing required member '{member}'"
    if seal["spec"] != SPEC_ID:
        return False, f"unknown spec id '{seal['spec']}'"
    if not isinstance(seal["causal_state"], dict) or not seal["causal_state"]:
        return False, "causal_state must be a non-empty object"
    for name, value in seal["causal_state"].items():
        if not any(name.startswith(c) for c in CLASSES):
            return False, f"parameter '{name}' outside defined classes"
        if not isinstance(value, str):
            return False, f"parameter '{name}' is not a string"
    expected = fingerprint(seal)
    if seal["fingerprint"] != expected:
        return False, f"fingerprint mismatch (expected {expected[:16]}…)"
    if output_text is not None:
        oh = hashlib.sha256(output_text.encode("utf-8")).hexdigest()
        if oh != seal["output_hash"]:
            return False, "output_hash does not match the provided output"
    return True, "seal verified (Level 1" + (" + output binding" if output_text is not None else "") + ")"


# ── CLI ───────────────────────────────────────────────────────────────────────
def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]

    if cmd == "demo":
        seal = emit_seal(
            emitter="reference-impl/1.0",
            causal_state={
                "identity.expert": "TECH",
                "engine.model": "demo-model",
                "shaping.depth": "3",
                "shaping.guard": "nominal",
            },
            output_text="Hello, governed world.",
            dictionary="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        print(json.dumps(seal, indent=2))
        ok, reason = verify_seal(seal, "Hello, governed world.")
        print(f"# self-verify: {ok} — {reason}")
        return 0 if ok else 1

    if cmd == "verify":
        seal = _load(args[0])
        output_text = None
        if "--output-text" in args:
            output_text = args[args.index("--output-text") + 1]
        elif "--output-file" in args:
            with open(args[args.index("--output-file") + 1], encoding="utf-8") as f:
                output_text = f.read()
        ok, reason = verify_seal(seal, output_text)
        print(("PASS: " if ok else "FAIL: ") + reason)
        return 0 if ok else 1

    if cmd == "selftest":
        d = args[0] if args else os.path.join(os.path.dirname(os.path.abspath(__file__)), "test-vectors")
        failures = 0
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json"):
                continue
            ok, reason = verify_seal(_load(os.path.join(d, name)))
            must_pass = name.startswith("valid")
            verdict = "OK" if ok == must_pass else "SELFTEST-FAILURE"
            if ok != must_pass:
                failures += 1
            print(f"{verdict:17s} {name}: verifier says {'PASS' if ok else 'FAIL'} ({reason}) — expected {'PASS' if must_pass else 'FAIL'}")
        print("selftest:", "ALL GOOD" if failures == 0 else f"{failures} failure(s)")
        return 0 if failures == 0 else 1

    print(__doc__)
    return 2


def cli() -> None:
    """Console entry point (`causal-seal ...` after pip install)."""
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    cli()
