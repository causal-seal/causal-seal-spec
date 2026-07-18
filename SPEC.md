# The Causal Seal Format

**An open specification for decision provenance in generative AI systems**

| | |
|---|---|
| **Version** | 1.0-draft |
| **Status** | Draft for community review |
| **Date** | 2026-07-17 |
| **Editor** | M. H. EL hamiani (BATEN Technologies, Rabat) |
| **License** | This specification text: CC BY 4.0. See §9 for implementation and IP notes. |
| **Companion paper** | [10.5281/zenodo.21431267](https://doi.org/10.5281/zenodo.21431267) |

---

## Abstract

Content-provenance standards (such as C2PA) answer the question *"where does this artifact come from?"*. Log-integrity protocols answer *"has this record been tampered with?"*. No open format today answers the question regulators have begun to ask of generative AI:***"why* did the system produce this specific output?"**

The Causal Seal is a compact, verifiable record bound to a single generated output. It cryptographically binds together (a) the output, (b) the set of **causal parameters** that governed its generation, and (c) the moment of emission. Any third party can verify the integrity of a seal without access to the underlying model. The format is model-agnostic, engine-agnostic, and designed to satisfy the technical core of emerging traceability obligations (EU AI Act Article 12, NIST AI RMF, and comparable regimes).

---

## 1. Scope

### 1.1 In scope
- The data model of a Causal Seal.
- The canonical serialization and fingerprint computation.
- The verification procedure (three levels).
- Conformance requirements for emitters and verifiers.
- An informative mapping to regulatory traceability obligations.

### 1.2 Out of scope
- **How an emitter produces a good causal state.** The governance mechanisms, steering methods, and calibrations that make a parameter genuinely causal are implementation concerns of the emitter, outside this specification. This document standardizes the *envelope of proof*, not the *engine of governance*.
- Content provenance of media artifacts (see C2PA).
- Proof of correct model execution (see zkML approaches).

---

## 2. Terminology

The key words MUST, MUST NOT, SHOULD, and MAY are to be interpreted as in RFC 2119.

**Output** — a single generated artifact (typically a text response) produced by a generative system in reply to an input.

**Causal parameter** — a named value satisfying the *causality criterion*: **had this parameter held a different value at generation time, the output could have been different.** Parameters that merely describe the output after the fact (word counts, readability scores) are *descriptive*, not causal, and MUST NOT be presented as causal.

**Causal state** — the complete set of causal parameters assembled by the emitter for one output, frozen at emission time.

**Seal** — the data object defined in §3, binding output, causal state and timestamp under one fingerprint.

**Emitter** — the system component that assembles the causal state and emits the seal at generation time.

**Verifier** — any party that checks a seal. Verification MUST be possible without access to the emitter's model weights or internal calibrations.

---

## 3. Data model

A Causal Seal is a JSON object with the following members:

```json
{
  "spec": "causal-seal/1.0",
  "emitter": "engine-name/version",
  "timestamp": "2026-07-17T14:00:00.000Z",
  "output_hash": "hex-encoded SHA-256 of the output (UTF-8)",
  "causal_state": {
    "identity.expert": "TECH",
    "identity.adapter": "adapter-name-v3",
    "identity.confidence": "0.87",
    "engine.model": "model-id",
    "field.subject": "dominant-subject-string",
    "field.regime": "stable",
    "shaping.depth": "3",
    "shaping.fluidity": "r3",
    "shaping.constraints": "3",
    "shaping.guard": "nominal",
    "context.memory_state": "awake",
    "context.buffer": "5",
    "context.condensed": "2"
  },
  "dictionary": "URL-or-hash of the emitter's parameter dictionary",
  "fingerprint": "hex-encoded SHA-256, computed as in §4",
  "signature": "optional — see §5.2"
}
```

### 3.1 Required members
`spec`, `emitter`, `timestamp`, `output_hash`, `causal_state`, `fingerprint` are REQUIRED. `dictionary` is REQUIRED for public verifiability of meaning (§3.3). `signature` is OPTIONAL (§5.2).

### 3.2 Causal parameter classes
Parameter names are namespaced by **class**. Six classes are defined; an emitter MUST cover at least the four marked ●:

| Class | Question answered | Examples |
|---|---|---|
| ● `identity.*` | *Who* answered — which expert/route/persona was selected, with what confidence | expert, adapter, confidence |
| ● `engine.*` | *With what* — which underlying model executed the text | model id |
| `field.*` | *Around what* — the semantic field state | dominant subject, regime |
| ● `shaping.*` | *How* — what shaped the form of the output | depth, fluidity, constraint filters, guard state |
| `context.*` | *Seeing what* — the context actually visible to the model | memory state, buffer, condensed count |
| ● *(implicit)* | *When* — the `timestamp` member | — |

All values are serialized as strings. Floating-point values MUST be quantized to a fixed number of decimals declared in the dictionary (non-determinism of float formatting breaks fingerprints).

### 3.3 The parameter dictionary
Sealed values are only auditable if their *meaning* is public. An emitter MUST publish a **dictionary** describing, for every parameter name it emits: its meaning, its value domain, and its quantization. The seal references this dictionary by URL or content-hash. The dictionary discloses *what a parameter means* — it need not disclose *how the emitter computes it*.

### 3.4 Extensibility
Emitters MAY add parameters within the defined classes or in an `x.*` vendor class. Verifiers MUST ignore unknown parameters when checking structure, and MUST include them when recomputing the fingerprint (the fingerprint covers the object as emitted).

---

## 4. Canonicalization and fingerprint

The fingerprint is computed as:

```
fingerprint = SHA-256( JCS( seal object minus "fingerprint" and "signature" ) )
```

where **JCS** is the JSON Canonicalization Scheme (RFC 8785): UTF-8, lexicographically sorted member names, no insignificant whitespace. This guarantees that two independent implementations serialize the same seal to the same bytes.

The `output_hash` member ensures the seal is bound to one exact output without requiring the output text to travel inside the seal (the output may be private; its hash is not).

---

## 5. Verification

### 5.1 Level 1 — Integrity
Recompute §4 over the received seal; compare with `fingerprint`. A match proves that **neither the causal state, nor the output binding, nor the timestamp has been altered since emission**. Level 1 requires nothing but the seal and the output (or its hash).

### 5.2 Level 2 — Authenticity (optional)
If `signature` is present, it MUST be an Ed25519 signature over the `fingerprint` by the emitter's published public key. Level 2 proves **which emitter** produced the seal. Integrity without authenticity answers *"is it intact?"*; with authenticity it answers *"and who says so?"*.

### 5.3 Level 3 — Causal audit (cooperative)
Where the emitter's governance path is deterministic, an auditor given the same input and declared state MUST be able to re-derive the same causal state (and, where the full decoding path is controlled, the same output). Level 3 is a property of the *emitter*, not the format; the format makes it checkable by giving the auditor a precise target to reproduce.

---

## 6. Conformance

**A conforming emitter:**
1. Emits a seal for **every** output at emission time — not on demand, not retroactively.
2. Includes only parameters that satisfy the causality criterion in `causal_state`, and publishes its dictionary.
3. Covers the four required classes (§3.2).
4. Computes the fingerprint exactly as in §4.

**A conforming verifier:**
1. Implements Level 1; implements Level 2 when a signature is present.
2. Rejects seals whose fingerprint does not match, whose required members are absent, or whose numeric values violate the declared quantization.
3. Treats verification failure as *"this seal proves nothing"* — not as proof of misconduct.

---

## 7. Security considerations

- **A seal proves binding, not virtue.** An emitter can seal meaningless parameters. The seal makes the emitter's claims *fixed and auditable*; whether those claims describe genuine causality is established by the dictionary, Level 3 audits, and the emitter's reputation or certification. This is the same trust structure as TLS: the padlock proves the channel, not the honesty of the merchant.
- **Timestamps** are asserted by the emitter. Deployments requiring trusted time SHOULD countersign seals with an RFC 3161 timestamp authority or anchor fingerprint batches in an external append-only log.
- **Descriptive smuggling.** Verifiers and certifiers SHOULD treat post-hoc metrics presented as causal parameters (violating §2) as a conformance failure.

---

## 8. Relationship to other work *(informative)*

| Approach | Question it answers | Relation |
|---|---|---|
| C2PA | Where does this *content* come from? | Complementary — different object (media artifact vs decision). |
| Hash-chained audit logs | Has the *record* been altered? | Necessary but weaker — protects the diary, says nothing about the *why*. A Causal Seal can be stored *in* such a log. |
| zkML | Was the *computation* performed correctly? | Orthogonal — proves execution of a model, not the provenance of the governing decision state. |
| Watermarking | Was this text machine-generated? | Orthogonal — detection, not explanation. |
| IETF SCITT | Is this *statement* registered on a transparency ledger? | Complementary — a Causal Seal is a natural payload for a SCITT signed statement; registration provides trusted time and non-equivocation (§7). |
| IETF RATS | Is the *environment* the one it claims to be? | Complementary — remote attestation of the emitter's runtime strengthens Level 2 into "which emitter, on which attested stack". |

---

## 9. IP and licensing note *(subject to legal review before publication)*

This specification text is licensed CC BY 4.0. Implementation of the **format** described here — assembling, serializing, fingerprinting and verifying seals per §3–§6 — is intended to be royalty-free for all. This specification grants **no license** to any particular governance, steering or state-computation mechanism used by an emitter to produce causal states; such mechanisms may be protected by patents of their respective implementers, including patent applications held by the editor's organization.

---

## 10. Regulatory mapping *(informative)*

| EU AI Act, Article 12 (record-keeping) | Causal Seal provision |
|---|---|
| Automatic recording of events over the system's lifetime | §6.1 — a seal per output, emitted automatically at generation time |
| Traceability of the system's functioning | §3.2 — the causal parameter classes: who, with what, around what, how, seeing what, when |
| Integrity of records | §4–§5.1 — fingerprint; any alteration invalidates the seal |
| Identification of risk-relevant situations | `shaping.guard` and `field.regime` — corrective and rupture events are sealed per output and filterable |
| Post-market monitoring | §5.2–§5.3 — authenticated, replayable audit across the deployment's life |
| **Article 19** — retention of automatically generated logs by providers | Seals are compact, self-verifying records suited to long-term retention; integrity survives storage migration (§4). |

Comparable mappings apply to NIST AI RMF (Govern/Measure functions) and to state-level US regimes requiring documentation of consequential automated decisions.

---

## Appendix A — Reference implementation

A production system emitting seals conformant with the spirit of this draft (predating its canonicalization, being aligned for v1.0) is publicly observable at chat.baten.ai. The free reference verifier is available at causalseal.org/verify.html and in this repository (`causal_seal.py`, `docs/verify.html`).

## Appendix B — Changelog

- **1.0-draft (2026-07-17)** — first complete draft.
