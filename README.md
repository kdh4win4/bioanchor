# BioAnchor 🔬⚓

**The Reproducibility & Provenance Layer for Bayesian Scientific Analysis**

[![PyPI](https://img.shields.io/pypi/v/bioanchor)](https://pypi.org/project/bioanchor/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19709077.svg)](https://doi.org/10.5281/zenodo.19709077)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> **BioAnchor is an autonomous scientific agent that executes Bayesian MCMC analyses, quantifies uncertainty, and permanently archives verifiable evidence on decentralized storage — creating a cryptographic chain-of-trust for scientific discovery.**

---

## Why BioAnchor?

Science has a **reproducibility crisis**. Over 70% of researchers have failed to reproduce another scientist's experiments (Nature, 2016). The root causes: lost data, opaque methods, and no verifiable provenance chain.

BioAnchor solves this by combining three capabilities that no other tool offers together:

- **Autonomous Bayesian Analysis** — Runs PyMC 5 / NUTS MCMC models with full posterior sampling and convergence diagnostics
- **Uncertainty Quantification** — Computes coefficient of variation (CV), R-hat, ESS, and credible intervals for every parameter
- **Permanent Decentralized Archiving** — Stores complete MCMC metadata (posteriors, diagnostics, model specs) on Arweave for immutable, censorship-resistant provenance

## How It Works

```
Raw Data → BioAnchor Agent → MCMC Analysis → Uncertainty Scores → Arweave Archive
                                                                      ↓
                                                              Permanent TX ID
                                                         (verifiable by anyone)
```

1. **Ingest** — Feed dose-response, genomic, or any biological dataset
2. **Analyze** — BioAnchor autonomously configures and runs Bayesian MCMC (PyMC 5, NUTS sampler)
3. **Quantify** — Generates uncertainty metrics (CV, posterior distributions, convergence diagnostics)
4. **Archive** — Permanently stores analysis metadata on Arweave with a unique Transaction ID
5. **Verify** — Anyone can retrieve and reproduce the analysis using the TX ID

## Quick Start

```bash
pip install bioanchor
```

```python
from bioanchor import BioAnchor

# Initialize with Arweave wallet
anchor = BioAnchor(wallet_path="arweave-wallet.json")

# Run MCMC analysis and archive results
result = anchor.analyze_and_archive(
    data=my_dataset,
    model_type="hill_equation",  # IC50 dose-response model
    n_samples=2000,
    n_chains=4
)

# Get permanent Arweave TX ID
print(f"Archived: {result.tx_id}")
print(f"Verify at: https://ar-io.dev/{result.tx_id}")
```

## Real-World Validation

BioAnchor has been validated with real pharmaceutical data:

- **IC50 dose-response modeling** using Hill equation with PyMC 5
- **4-chain NUTS sampling** with full convergence diagnostics
- **Live Arweave archive**: [`2lIZtjsu120ERqPKu6XbITpUnAveWeH7hI4owBfNCdY`](https://ar-io.dev/2lIZtjsu120ERqPKu6XbITpUnAveWeH7hI4owBfNCdY)

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 BioAnchor Agent                  │
├─────────────────────────────────────────────────┤
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐ │
│  │  PyMC 5   │  │ ArviZ    │  │  Uncertainty │ │
│  │  Engine   │→ │Diagnostics│→│  Scoring     │ │
│  │ (NUTS)    │  │ (R-hat,  │  │  (CV, CI,    │ │
│  │           │  │  ESS)    │  │   posterior)  │ │
│  └───────────┘  └──────────┘  └──────┬───────┘ │
│                                       │         │
│  ┌────────────────────────────────────▼───────┐ │
│  │         Decentralized Storage Layer        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │ │
│  │  │ Arweave  │  │ Filecoin │  │  IPFS    │ │ │
│  │  │ (live)   │  │ (planned)│  │(planned) │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘ │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## DeSci Integration Roadmap

BioAnchor is designed to be the **scientific truth verification layer** for the decentralized science (DeSci) ecosystem:

### Phase 1: Multi-Chain Storage (Current → Q3 2026)
- ✅ Arweave permanent archiving (live)
- 🔄 Filecoin/IPFS bridge (in development)
- 🔄 Multi-chain verification endpoints

### Phase 2: IP-NFT & Data Quality Oracle (Q3–Q4 2026)
- Uncertainty-weighted reliability scoring for IP-NFTs
- Integration with Molecule / BIO Protocol IP framework
- CV-based data quality oracle for BioDAOs (VitaDAO, AthenaDAO, etc.)

### Phase 3: Autonomous Bayesian Scientist Agent (Q4 2026+)
- AI-driven hypothesis generation from literature
- Automated MCMC model selection and execution
- Self-archiving results with provenance chain
- Integration with BIO Protocol Scientific AI Agent platform

### Phase 4: DAO Governance & Token Economy (2027)
- Community-governed research prioritization
- Staking on reproducibility verification
- Token-incentivized peer review of MCMC analyses

## For BioDAOs & DeSci Projects

BioAnchor provides a **trust layer** that any BioDAO can plug into:

| Use Case | How BioAnchor Helps |
|---|---|
| **Drug Discovery** | Verify IC50/EC50 dose-response analyses with full uncertainty quantification |
| **IP-NFT Valuation** | Score data quality using CV metrics before tokenizing research IP |
| **Reproducibility Audits** | Retrieve and re-run any archived MCMC analysis from its Arweave TX ID |
| **Grant Accountability** | Prove research outputs are real and verifiable on-chain |

## Testing

BioAnchor includes a `MockUploader` for development and testing without Arweave wallet:

```python
from bioanchor import BioAnchor, MockUploader

anchor = BioAnchor(uploader=MockUploader())
result = anchor.analyze_and_archive(data=test_data)
# Returns simulated TX ID for testing
```

## Tech Stack

- **Python 3.11+** with PyMC 5, ArviZ, SciPy
- **Arweave** via ar-io.dev gateway (Node.js uploader for production)
- **Zenodo** DOI: [10.5281/zenodo.19709077](https://doi.org/10.5281/zenodo.19709077)

## Citation

If you use BioAnchor in your research, please cite:

```bibtex
@software{kim2026bioanchor,
  author       = {Kim, Dohoon},
  title        = {BioAnchor: Bridging Bayesian Biological Data Analysis with Decentralized Storage},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19709077},
  url          = {https://doi.org/10.5281/zenodo.19709077}
}
```

## About

**BioAnchor** is developed by [Dohoon Kim](mailto:dkim@promptgenix.org) at [Promptgenix LLC](https://promptgenix.org), building open-source scientific infrastructure for verifiable, reproducible research.

- 📦 PyPI: [`pip install bioanchor`](https://pypi.org/project/bioanchor/)
- 🔗 GitHub: [github.com/kdh4win4/bioanchor](https://github.com/kdh4win4/bioanchor)
- 📄 Paper: Submitted to *Bioinformatics* (Oxford) — BIOINF-2026-1271

## License

MIT License — see [LICENSE](LICENSE) for details.
