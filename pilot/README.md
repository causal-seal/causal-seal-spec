---
license: cc-by-4.0
tags:
- provenance
- ai-transparency
- causal-seal
pretty_name: Causal Seal — reference pilot
configs:
- config_name: default
  data_files:
  - split: train
    path: trace.jsonl
---
# Causal Seal — reference pilot

An illustrative, self-contained snapshot showing the full chain a third party can
follow **without knowing the implementation that emitted it**:

    exact commit SHA
        -> download / verify this snapshot
        -> open the STS trace (trace.jsonl)
        -> follow `causal_seal_ref` -> seal.json
        -> install / run the published verifier

## Files
| file | role |
|---|---|
| `manifest.json` | entry point: what maps to what, sha256 per file. Git provides snapshot integrity; the manifest is *not* a second integrity system. |
| `trace.jsonl` | STS-format session trace. The session header carries `causal_seal_ref`, `causal_seal_profile`, `output_sha256` (extra metadata the STS renderer ignores). |
| `seal.json` | the Causal Seal (`causal-seal/1.0`): binds the output hash + governing state + emission time into a fingerprint. |
| `causal-profile.json` | the parameter dictionary: meaning, domain and **authority** (observed / asserted / derived / attested) of each governing-state field. The seal commits to this file **by content hash** (`dictionary`). |

## Verify it yourself
The reference verifier is published as a package (not shipped inside this snapshot):

    pip install causal-seal

    causal-seal verify seal.json --output-text "Helsinki is the capital of Finland."

Reference implementation & spec: https://github.com/causal-seal/causal-seal-spec

Snapshot integrity (Hugging Face CLI), against an exact commit:

    hf cache verify <repo-id> --repo-type dataset --revision <full-commit-sha> \
      --fail-on-missing-files --fail-on-extra-files

## What this pilot deliberately does NOT claim
- **model_revision** is honestly marked *alias-only* (no immutable revision was exposed).
- The seal proves **(a)** the record is internally consistent with its fingerprint. It does **not**, by itself, prove **(b)** the referenced output is present/authentic, nor completeness/ordering of a set of seals — those belong to output retrieval and to an external transparency/log layer.
- `engine.model` here is *asserted* (see `causal-profile.json` authority).

Self-verify at build time: **True** — seal verified (Level 1 + output binding)
