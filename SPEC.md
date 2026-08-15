# Dynamic Pairwise Schema Compatibility Graph Specification

## Overview

The `Dynamic Pairwise Schema Compatibility Graph` Intelligent Contract maintains an on-chain directed graph of API and RPC schemas. It retrieves schemas over multi-gateway HTTPS URLs, executes semantic LLM compatibility analysis under GenLayer strict consensus (`gl.eq_principle.strict_eq`), and enforces deterministic invariants between compatibility status, breaking change counts, and change lists.

---

## Invariants & Deterministic Decision Matrix

1. **Fail Closed on Missing/Empty Content**:
   - If both gateways return empty or undecodable content for either schema, the contract immediately sets `status_code = u256(4)` (`EVALUATION_FAILED`), `breaking_change_count = 0`, and records `EVALUATION_FAILED: Empty schema content from gateways`.
2. **Reconciliation of Breaking Change Count**:
   - `breaking_change_count = len(breaking_changes_list)`.
3. **Strict Status / Count Invariant**:
   - If `breaking_change_count > 0` or `len(breaking_changes_list) > 0`, status **CANNOT** be `COMPATIBLE` or `BACKWARD_COMPATIBLE_ONLY`. The contract strictly forces `status_code = u256(3)` (`BREAKING_INCOMPATIBLE`).
   - Only when `breaking_change_count == 0` AND `len(breaking_changes_list) == 0`:
     - `COMPATIBLE` -> `status_code = u256(1)`
     - `BACKWARD_COMPATIBLE_ONLY` -> `status_code = u256(2)`

| Status Code | Status Name | Breaking Changes Count | Change List | Condition |
| :--- | :--- | :--- | :--- | :--- |
| `u256(1)` | `COMPATIBLE` | `0` | Empty | Fully bidirectional compatible |
| `u256(2)` | `BACKWARD_COMPATIBLE_ONLY` | `0` | Empty | Spec B extends Spec A without breaking changes |
| `u256(3)` | `BREAKING_INCOMPATIBLE` | `>= 1` | Non-empty | Contains at least 1 breaking change |
| `u256(4)` | `EVALUATION_FAILED` | `0` | Empty | Failed to retrieve schema from gateways |

---

## Canonical Validator Signature & Binding

```text
SPECS:{spec_a_id}:{spec_b_id}|STATUS:{status_code}|COUNT:{breaking_change_count}|SUMMARY:{normalized_summary}|TRUNC_A:{source_a_truncated}|TRUNC_B:{source_b_truncated}
```
