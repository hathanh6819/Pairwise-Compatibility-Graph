# Pairwise Compatibility Graph (GenLayer Intelligent Contract)

An auditable, decentralized graph primitive for evaluating pairwise API and smart contract schema compatibility using multi-gateway evidence retrieval and LLM semantic diff classification on GenLayer.

---

## Architecture Difference Statement (Originality Gate)

Unlike generic document analysis or single-bundle evaluation primitives, this contract implements a **Pairwise Edges Compatibility Graph (`PairwiseEdgeRecord`)**.

- **Acquisition Flow**: Dual independent multi-gateway retrieval (Primary + Fallback URLs) for both Spec A and Spec B.
- **Lifecycle**: Strict 2-phase lifecycle (`SPEC_REGISTERED` -> `EDGE_EVALUATED`) with idempotency and cross-spec evaluation guards.
- **Storage Model**: Independent `TreeMap[u256, SpecRecord]` for registered specifications and `TreeMap[u256, PairwiseEdgeRecord]` for evaluated pairwise edges.
- **Validator Design**: Strict equivalence (`gl.eq_principle.strict_eq`) over an exact canonical validator signature binding spec IDs, status codes, breaking change counts, normalized summaries, and source truncation flags.
- **Integration Behavior**: Serves as a decentralised operational gate for cross-chain relayers, dApp aggregators, and microservices to query `check_compatibility(spec_a_id, spec_b_id)` before processing payloads.

---

## Why GenLayer?

Traditional smart contracts cannot parse complex OpenAPI specs or determine whether a parameter type change constitutes a breaking operational change. Off-chain centralized services introduce single-point-of-failure vulnerabilities for Web3 protocol composability. GenLayer enables validators to independently fetch schemas, run semantic analysis, and reach consensus on breaking changes before persisting the compatibility status on-chain.

---

## Public API Reference

### Write Methods

- **`register_spec(name: str, version: str, primary_url: str, fallback_url: str) -> u256`**
  Registers a new API/protocol specification with primary and fallback gateway URLs. Returns `spec_id`.

- **`evaluate_compatibility(spec_a_id: u256, spec_b_id: u256) -> u256`**
  Fetches schemas for Spec A and Spec B across gateways, runs non-deterministic consensus evaluation, derives status code, and records the edge. Returns `edge_id`.

### View Methods

- **`get_spec(spec_id: u256) -> typing.Any`**
  Returns details of a registered spec as a dictionary.

- **`get_edge(spec_a_id: u256, spec_b_id: u256) -> typing.Any`**
  Returns details of an evaluated pairwise edge including `validator_signature`.

- **`check_compatibility(spec_a_id: u256, spec_b_id: u256) -> str`**
  Returns `"COMPATIBLE"`, `"BACKWARD_COMPATIBLE_ONLY"`, `"BREAKING_INCOMPATIBLE"`, or `"NOT_EVALUATED"`.

---

## Lifecycle & State Machine

```text
[ Unregistered Specs ]
        │
        ▼ (register_spec)
 [ SPEC_REGISTERED ]  ─── (evaluate_compatibility) ───► [ EDGE_EVALUATED ]
                                                              │
                                                              ▼
                                                    (check_compatibility)
```

---

## Deployment Evidence

- **Deployed Contract Address**: [`0xD4D57ea03762E1A6c181B626387c5116d4b2E245`](file:///d:/Genlayer%20Dino/pairwise-compatibility-graph/evidence/deployed_address.txt)
- **Deployment Status**: `FINALIZED` on GenLayer Studio Network.

## Pre-Submission Verification

Before Studio deployment, run the local verification suite:

```bash
# 1. AST compilation check
python -m py_compile contracts/pairwise_compatibility_graph.py

# 2. Static header & ASCII scan
python tests/test_static.py

# 3. Direct mode functional & differential validator tests
python tests/test_contract.py
```

---

## Honest Limitations

1. **Gateway Availability**: If both primary and fallback gateways for a spec are offline, evaluation fails closed.
2. **Schema Size Bounds**: Schemas exceeding 4,000 characters are truncated; `source_a_truncated` or `source_b_truncated` flags will be set to `True`.
