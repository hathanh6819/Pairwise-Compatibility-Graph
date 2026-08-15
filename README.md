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

## Deployment Status & On-Chain Lifecycle Evidence

- **GitHub Repository**: [`https://github.com/hathanh6819/Pairwise-Compatibility-Graph`](https://github.com/hathanh6819/Pairwise-Compatibility-Graph)
- **Deployed Contract Address**: [`0xD412ec7C0dEB52260E43590a2Cd88f06CCdCDb97`](https://explorer-studio.genlayer.com/address/0xD412ec7C0dEB52260E43590a2Cd88f06CCdCDb97)
- **Creator Address**: `0xa365F55A3bf352767bc5c5739FfDDAee8FcF3a19`
- **Deployment Status**: `FINALIZED` on GenLayer Studionet (Chain ID 61999) with full 4-transaction lifecycle history verified on GenLayer Explorer (100% SUCCESS and MAJORITY_AGREE Consensus):
  1. `deploy_contract`: [`0xD412ec7C...`](https://explorer-studio.genlayer.com/address/0xD412ec7C0dEB52260E43590a2Cd88f06CCdCDb97) (`SUCCESS`, `Accepted`)
  2. `register_spec` (Spec A): [`0xc028516d...`](https://explorer-studio.genlayer.com/tx/0xc028516de74513dfd96f2c043d45ff6f99ed4cce133985c9a8ef1124a66e8c27) (`SUCCESS`, `Accepted`)
  3. `register_spec` (Spec B): [`0x586c2a6e...`](https://explorer-studio.genlayer.com/tx/0x586c2a6e2b95b1c2f8662b1384d7cf7b7c5de411eb7d1ce5ea0eb7b028b30d2c) (`SUCCESS`, `Accepted`)
  4. `evaluate_compatibility`: [`0x7e355b87...`](https://explorer-studio.genlayer.com/tx/0x7e355b87703457bbe8feb3de71c861f629380ae4f267334275cda4f424c93b19) (`SUCCESS`, `Accepted`)
