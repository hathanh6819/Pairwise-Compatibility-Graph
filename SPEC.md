# Pairwise Compatibility Graph Technical Specification

## Overview

The Pairwise Compatibility Graph is a GenLayer Intelligent Contract primitive designed to evaluate, verify, and persist pairwise schema compatibility states between API or protocol specifications (OpenAPI, JSON-RPC, GraphQL schemas).

It fetches schemas from dual independent web gateways for Spec A and Spec B, invokes LLM semantic classification via GenLayer strict consensus (`gl.eq_principle.strict_eq`), derives normalized status codes deterministically, and binds all consequential fields into an auditable validator signature on-chain.

---

## Input Boundaries & Storage Limits

- **Spec Name**: 1 to 64 ASCII characters.
- **Spec Version**: 1 to 32 ASCII characters.
- **Gateway URLs (Primary & Fallback)**: 1 to 512 ASCII characters.
- **Max Schema Fetch Payload**: 4,000 UTF-8 characters per source gateway. Payload exceeding 4,000 characters triggers `source_a_truncated` or `source_b_truncated` flags.
- **Normalized Summary String**: Bounded to 256 ASCII characters.

---

## Storage Invariants

1. `spec_count`: Strict append-only counter for registered API specs.
2. `edge_count`: Strict append-only counter for evaluated pairwise edge records.
3. `specs`: `TreeMap[u256, SpecRecord]` maps `spec_id` to `SpecRecord`.
4. `edges`: `TreeMap[u256, PairwiseEdgeRecord]` maps `edge_id` to `PairwiseEdgeRecord`.
5. `pair_to_edge`: `TreeMap[u256, u256]` maps composite pair key `(spec_a_id * 1000000 + spec_b_id)` to `edge_id`.
6. Self-Evaluation Invariant: `spec_a_id != spec_b_id` enforced before execution.

---

## Decision Matrix & Status Codes

| Status String | Breaking Change Count | Derived `status_code` | Human Description |
| --- | --- | --- | --- |
| `COMPATIBLE` | `0` | `u256(1)` | Full backward and forward compatibility. |
| `BACKWARD_COMPATIBLE_ONLY` | `>= 0` | `u256(2)` | Backward compatible only (new optional fields added). |
| `BREAKING_INCOMPATIBLE` | `> 0` | `u256(3)` | Breaking changes detected (removed fields, altered types). |

---

## Validator Signature & Consensus Binding Matrix

To ensure leader and validator nodes agree on exact semantic meaning rather than superficial JSON formatting, the contract builds a canonical signature string:

```text
SPECS:{spec_a_id}:{spec_b_id}|STATUS:{status_code}|COUNT:{breaking_change_count}|SUMMARY:{normalized_summary}|TRUNC_A:{source_a_truncated}|TRUNC_B:{source_b_truncated}
```

### Consensus Binding Matrix

| Field | Origin | Persisted? | Downstream Effect | Validator Binding | Differential Test |
| --- | --- | --- | --- | --- | --- |
| `status_code` | LLM + deterministic derivation | Yes | Core execution gate | Included in `validator_signature` | Mutate status -> validator rejects |
| `breaking_change_count` | LLM + schema validator | Yes | Severity filter | Included in `validator_signature` | Mutate count -> validator rejects |
| `normalized_summary` | LLM + text canonicalization | Yes | Auditable evidence | Included in `validator_signature` | Mutate summary text -> validator rejects |
| `source_a_truncated` | Web fetch decoder | Yes | Data completeness flag | Included in `validator_signature` | Mutate flag -> validator rejects |
| `source_b_truncated` | Web fetch decoder | Yes | Data completeness flag | Included in `validator_signature` | Mutate flag -> validator rejects |

---

## Downstream Integrations

Integrator dApps and cross-chain relayers query `check_compatibility(spec_a_id, spec_b_id)`:
- Returns `"COMPATIBLE"` -> Safe to execute transaction or route message.
- Returns `"BREAKING_INCOMPATIBLE"` -> Rejects execution and triggers error circuit breaker.
