# Deployment & On-Chain Consensus Evidence

This folder holds finalized deployment artifacts and verified on-chain lifecycle transaction evidence for the `Dynamic Pairwise Schema Compatibility Graph Primitive` Intelligent Contract on GenLayer Studionet.

## Deployment Information

- **Contract Name**: `PairwiseCompatibilityGraph`
- **Deployed Contract Address**: [`0xD412ec7C0dEB52260E43590a2Cd88f06CCdCDb97`](https://explorer-studio.genlayer.com/address/0xD412ec7C0dEB52260E43590a2Cd88f06CCdCDb97)
- **Creator Address**: `0xa365F55A3bf352767bc5c5739FfDDAee8FcF3a19`
- **Deployment Status**: `FINALIZED` (100% SUCCESS and MAJORITY_AGREE Consensus across all transactions)
- **Compiler Version**: `# v0.2.16`
- **Runner Dependency**: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

---

## On-Chain Lifecycle Transactions (Verified on GenLayer Explorer)

| Step | Method / Action | Transaction Hash | GenVM Result | Consensus Result |
| --- | --- | --- | --- | --- |
| 1 | `(construct...)` [Deploy] | [`0xD412ec7C0dEB52260E43590a2Cd88f06CCdCDb97`](https://explorer-studio.genlayer.com/address/0xD412ec7C0dEB52260E43590a2Cd88f06CCdCDb97) | `SUCCESS` | `Accepted` |
| 2 | `register_spec` (Spec A) | [`0xc028516de74513dfd96f2c043d45ff6f99ed4cce133985c9a8ef1124a66e8c27`](https://explorer-studio.genlayer.com/tx/0xc028516de74513dfd96f2c043d45ff6f99ed4cce133985c9a8ef1124a66e8c27) | `SUCCESS` | `Accepted` |
| 3 | `register_spec` (Spec B) | [`0x586c2a6e2b95b1c2f8662b1384d7cf7b7c5de411eb7d1ce5ea0eb7b028b30d2c`](https://explorer-studio.genlayer.com/tx/0x586c2a6e2b95b1c2f8662b1384d7cf7b7c5de411eb7d1ce5ea0eb7b028b30d2c) | `SUCCESS` | `Accepted` |
| 4 | `evaluate_compatibility` | [`0x7e355b87703457bbe8feb3de71c861f629380ae4f267334275cda4f424c93b19`](https://explorer-studio.genlayer.com/tx/0x7e355b87703457bbe8feb3de71c861f629380ae4f267334275cda4f424c93b19) | `SUCCESS` | `Accepted` |

## Evidence Files

- [`deployed_address.txt`](file:///d:/Genlayer%20Dino/pairwise-compatibility-graph/evidence/deployed_address.txt): Raw deployed contract address.
