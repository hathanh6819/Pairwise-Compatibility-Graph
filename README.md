# Dynamic Pairwise Schema Compatibility Graph (GenLayer Intelligent Contract)

An on-chain directed graph of API/RPC schema versions that independently fetches schema definitions over HTTPS dual gateways, verifies semantic backward compatibility using decentralized LLM validators under strict consensus, and enforces rigid status/count/change-list invariants.

---

## Purpose & Originality

Modern decentralized architectures rely on APIs and RPC interfaces that evolve continuously. Traditional smart contracts cannot parse complex JSON/OpenAPI schema definitions to check if version upgrades break downstream consumers.

`PairwiseCompatibilityGraph` uses GenLayer Intelligent Contracts to:
1. Multi-gateway fetch schema specifications (primary and fallback URLs).
2. Fail closed if schemas cannot be retrieved (`EVALUATION_FAILED`).
3. Evaluate breaking changes through decentralized LLM consensus.
4. Strictly enforce invariants: `COMPATIBLE` results can never carry positive breaking change counts.

---

## Public API Reference

### Write Methods
- **`register_spec(name: str, version: str, primary_url: str, fallback_url: str) -> u256`**
  Registers an API/RPC schema version with primary and fallback gateway URLs.
- **`evaluate_compatibility(spec_a_id: u256, spec_b_id: u256) -> u256`**
  Executes multi-gateway retrieval and LLM evaluation under strict consensus. Enforces consistency invariants.

### View Methods
- **`get_spec(spec_id: u256) -> typing.Any`**
- **`get_edge(spec_a_id: u256, spec_b_id: u256) -> typing.Any`**
- **`check_compatibility(spec_a_id: u256, spec_b_id: u256) -> str`**
  Returns `"COMPATIBLE"`, `"BACKWARD_COMPATIBLE_ONLY"`, `"BREAKING_INCOMPATIBLE"`, `"EVALUATION_FAILED"`, or `"NOT_EVALUATED"`.

---

## Consensus & Deterministic Invariants

- **Status / Count / Change-List Invariant**:
  - `breaking_change_count` is strictly derived as `len(breaking_changes_list)`.
  - If `count > 0`, status MUST be `BREAKING_INCOMPATIBLE` (3).
  - Status `COMPATIBLE` (1) and `BACKWARD_COMPATIBLE_ONLY` (2) are allowed ONLY when `count == 0` and `breaking_changes` is empty.
  - If either spec schema returns empty content from all gateways, the contract fails closed into `EVALUATION_FAILED` (4).

---

## Local Verification Commands

```bash
# 1. Static header & pure ASCII check
python tests/test_static.py

# 2. Direct mode functional, invariant, & differential tests
python tests/test_contract.py
```

---

## Deployment Status

- **GitHub Repository**: [`https://github.com/hathanh6819/Pairwise-Compatibility-Graph`](https://github.com/hathanh6819/Pairwise-Compatibility-Graph)
- **Deployment Status**: Updated for resubmission following Steward feedback.
