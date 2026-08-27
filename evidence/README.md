# Deployment & On-Chain Consensus Evidence

This folder holds finalized deployment artifacts and verified on-chain lifecycle transaction evidence for the `Dynamic Pairwise Schema Compatibility Graph Primitive` Intelligent Contract on GenLayer Studionet.

## Deployment Information

- **Contract Name**: `PairwiseCompatibilityGraph`
- **Deployed Contract Address**: [`0x0EBe00EC7127c940E0Dca43DC8e4dD5b429115A4`](https://explorer-studio.genlayer.com/address/0x0EBe00EC7127c940E0Dca43DC8e4dD5b429115A4)
- **Deployment Status**: `FINALIZED` (100% SUCCESS and MAJORITY_AGREE Consensus across all transactions)
- **Compiler Version**: `# v0.2.16`
- **Runner Dependency**: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

---

## On-Chain Lifecycle Transactions (Verified on GenLayer Explorer)

| Step | Method / Action | Transaction Hash | GenVM Result | Consensus Result |
| --- | --- | --- | --- | --- |
| 1 | `(construct...)` [Deploy] | [`0x0EBe00EC7127c940E0Dca43DC8e4dD5b429115A4`](https://explorer-studio.genlayer.com/address/0x0EBe00EC7127c940E0Dca43DC8e4dD5b429115A4) | `SUCCESS` | `Accepted` |
| 2 | `register_spec` (Spec A) | [`0xc84990ecf422e63ec2e511d22e88008978855e8883d161bf1deb730ad3df7150`](https://explorer-studio.genlayer.com/tx/0xc84990ecf422e63ec2e511d22e88008978855e8883d161bf1deb730ad3df7150) | `SUCCESS` | `Accepted` |
| 3 | `register_spec` (Spec B) | [`0x44e5870c38c0939c9d15bcbbdd3d9699aed36c09284dbd004ce767e69efc74b1`](https://explorer-studio.genlayer.com/tx/0x44e5870c38c0939c9d15bcbbdd3d9699aed36c09284dbd004ce767e69efc74b1) | `SUCCESS` | `Accepted` |
| 4 | `evaluate_compatibility` | [`0x888ba62d53dcb29d6ba9c018277cdebea3835888f84b10bce6453acbc3da361c`](https://explorer-studio.genlayer.com/tx/0x888ba62d53dcb29d6ba9c018277cdebea3835888f84b10bce6453acbc3da361c) | `SUCCESS` | `Accepted` |

## Evidence Files

- [`deployed_address.txt`](file:///d:/Genlayer%20Dino/pairwise-compatibility-graph/evidence/deployed_address.txt): Raw deployed contract address.
