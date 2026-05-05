# BioAnchor Roadmap

> **Maintainer:** Dohoon Kim ([@kdh4win4](https://github.com/kdh4win4)) · Promptgenix LLC  
> **Last updated:** 2026-05-03  
> **Status legend:** ✅ Shipped · 🔨 In Progress · 📋 Planned · 💡 Exploring

---

## v0.1.0 — Foundation (✅ Shipped)

- Bayesian MCMC analysis pipeline (PyMC 5, NUTS sampler)
- Automated MCMC diagnostics extraction (R-hat, ESS, divergences)
- Arweave permanent archival of analysis metadata
- MockUploader for offline testing
- Published on PyPI (`pip install bioanchor`)
- Zenodo DOI: [10.5281/zenodo.19709077](https://doi.org/10.5281/zenodo.19709077)

---

## v0.2.0 — On-Chain Verification Layer (📋 Planned)

Add trustless, on-chain recording of MCMC reliability scores so that analysis results are not only permanently stored but independently verifiable.

- **MCMC diagnostics hashing** — deterministic hash of convergence diagnostics (R-hat, ESS, trace summaries) to create a tamper-proof fingerprint of each analysis run
- **Smart contract integration** — record reliability scores, diagnostic hashes, and dataset identifiers on-chain (chain candidates under evaluation: SUI, Solana, Ethereum L2)
- **On-chain ↔ Arweave cross-referencing** — link the on-chain verification record to the corresponding Arweave transaction ID for full provenance
- **Verification API** — `bioanchor.verify()` endpoint to validate that a stored analysis matches its on-chain record

---

## v0.3.0 — Multi-Backend Storage (📋 Planned)

Expand permanent storage beyond Arweave to support emerging decentralized storage networks.

- **Walrus storage adapter** — add Walrus (SUI ecosystem) as an alternative/complementary archival backend
- **Storage abstraction layer** — unified `StorageBackend` interface so users can plug in Arweave, Walrus, or future providers
- **Redundant archival mode** — option to simultaneously archive to multiple backends for maximum durability

---

## v0.4.0 — Stan Integration & Multi-Sampler Support (📋 Planned)

- **Stan / CmdStanPy support** — extend beyond PyMC to support Stan-based MCMC workflows
- **Sampler-agnostic diagnostics** — unified diagnostics extraction regardless of backend sampler
- **NumPyro / JAX support** — lightweight adapter for NumPyro models

---

## v0.5.0 — AI Agent Integration API (💡 Exploring)

Enable external AI agents and autonomous research pipelines to invoke BioAnchor as a validation module.

- **Agent-callable API** — structured input/output interface for programmatic MCMC validation requests
- **Batch validation mode** — process multiple hypotheses/datasets in a single call
- **Confidence scoring schema** — standardized JSON output of reliability scores consumable by downstream agents
- **Webhook / callback support** — notify agents when long-running MCMC analyses complete

---

## Future Directions (💡 Exploring)

- Interactive dashboard for visual exploration of archived analyses
- Federated analysis registry — cross-lab discovery of archived MCMC results
- DAO-based governance for community-curated validation standards
- Integration with DeSci funding and review protocols

---

## Contributing

BioAnchor is open source. If you're interested in contributing to any of the above, please open an issue or discussion on [GitHub](https://github.com/kdh4win4/bioanchor).
