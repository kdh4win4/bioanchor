# BioAnchor 🔬⛓️

**Permanent, verifiable archiving of Bayesian/MCMC analysis artifacts on Arweave.**

[![PyPI version](https://badge.fury.io/py/bioanchor.svg)](https://badge.fury.io/py/bioanchor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## The Problem

Bayesian and MCMC analyses in computational biology are **nearly impossible to reproduce**:

- Raw MCMC chains are large and rarely shared
- Zenodo, GitHub, and NCBI can delete or restrict data
- There is no standard for what constitutes a "reproducible" Bayesian analysis artifact
- Drug discovery and genomics data have provenance and audit requirements that no current tool addresses

## The Solution

BioAnchor defines a **minimal, standardised manifest** of everything needed to verify and re-run a Bayesian analysis, then uploads it to [Arweave](https://arweave.org) — a decentralised storage network where data is **permanent and immutable**.

You do **not** upload raw data (privacy + cost). You upload:

- SHA-256 hash of input data (proof of what was used)
- MCMC configuration: sampler, chains, draws, seed, priors
- Posterior summary statistics (mean, SD, R̂, ESS)
- Software environment fingerprint

This is typically **< 5 KB** — negligible cost on Arweave.

The Arweave TX ID goes into your paper alongside the DOI. Anyone can verify the analysis, check convergence, and reproduce results with the same seed.

---

## Quick Start

```bash
pip install bioanchor[all]
```

### With PyMC

```python
import pymc as pm
from bioanchor import BioAnchor

with pm.Model() as model:
    alpha = pm.Normal("alpha", 0, 1)
    beta  = pm.HalfNormal("beta", 1)
    # ... your model ...
    idata = pm.sample(2000, random_seed=42)

ba = BioAnchor(wallet_path="wallet.json")

tx_id = ba.archive_pymc(
    idata=idata,
    model=model,
    seed=42,
    data=X,                                        # numpy array, hashed not uploaded
    data_description="TCGA-BRCA expression matrix (n=500, p=200)",
    data_source="TCGA",
    title="Sparse Bayesian regression for drug target identification",
    authors=["Your Name <you@uni.ac.kr>"],
    domain="drug_discovery",
    tags=["sparse-regression", "drug-target", "tcga"],
)

print(f"https://arweave.net/{tx_id}")
# → Add this URL to your Methods section
```

### CLI

```bash
# Generate a manifest template
bioanchor init --output my_analysis.json

# Upload to Arweave (edit the template first)
bioanchor upload --manifest my_analysis.json --wallet wallet.json

# Verify an uploaded manifest
bioanchor verify xK9mP2abc...

# Check wallet balance
bioanchor balance --wallet wallet.json
```

### Development / Testing (no wallet needed)

```python
ba = BioAnchor(mock=True)   # uses MockUploader, prints fake TX ID
tx_id = ba.archive_pymc(idata, seed=42, data=X, title="Test")
```

---

## Manifest Format

The manifest is a small JSON file (~2–5 KB). This is the **core scientific contribution** of BioAnchor.

```json
{
  "schema_version": "1.0",
  "bioanchor_version": "0.1.0",
  "created_at": "2026-04-16T09:00:00+00:00",
  "title": "Bayesian dose-response IC50 estimation",
  "authors": ["Author Name"],
  "analysis_type": "MCMC",
  "domain": "drug_discovery",
  "tags": ["dose-response", "ic50", "hill-equation"],
  "software": {
    "language": "Python 3.11.0",
    "packages": { "pymc": "5.9.0", "arviz": "0.18.0", "numpy": "1.26.0" }
  },
  "data": {
    "sha256": "de2fb170...",
    "description": "12-point IC50 curve (log10 μM, % activity)",
    "n_samples": 12,
    "n_features": 2,
    "source": "synthetic"
  },
  "mcmc": {
    "sampler": "NUTS",
    "n_chains": 4,
    "n_draws": 2000,
    "n_warmup": 1000,
    "seed": 42,
    "prior_spec": {
      "log_ic50": "Normal(mu=-0.3, sigma=1.0)",
      "hill_n":   "HalfNormal(sigma=2.0)"
    },
    "posterior_mean": { "log_ic50": -0.31, "ic50": 0.49, "hill_n": 1.79 },
    "posterior_std":  { "log_ic50": 0.09,  "ic50": 0.10, "hill_n": 0.21 },
    "r_hat":          { "log_ic50": 1.001, "ic50": 1.001, "hill_n": 1.003 },
    "ess_bulk":       { "log_ic50": 892.0, "ic50": 887.0, "hill_n": 755.0 },
    "divergences": 0,
    "acceptance_rate": 0.93
  }
}
```

---

## Why Arweave?

| Storage | Permanent? | Immutable? | Decentralised? |
|---------|-----------|-----------|---------------|
| GitHub  | ✗ (account deletion) | ✗ | ✗ |
| Zenodo  | ✗ (operator control) | ✗ | ✗ |
| IPFS    | ✗ (requires pinning) | ✓ | ✓ |
| **Arweave** | **✓ (mathematical guarantee)** | **✓** | **✓** |

Arweave's endowment model guarantees storage for a minimum of 200 years. A 5 KB manifest costs ~$0.0001 USD to archive permanently.

---

## Arweave Wallet Setup

1. Go to [arweave.app](https://arweave.app) and generate a wallet
2. Download the JWK JSON file (`wallet.json`)
3. Fund with a small amount of AR (~0.01 AR is enough for thousands of uploads)
4. Use `bioanchor balance --wallet wallet.json` to check

For testnet experimentation, use [Irys devnet](https://docs.irys.xyz/developer-docs/devnet).

---

## Supported Integrations

| Framework | Status |
|-----------|--------|
| PyMC 5.x  | ✅ Full integration |
| ArviZ     | ✅ (via PyMC) |
| Stan/CmdStanPy | 🔜 Planned |
| NumPyro   | 🔜 Planned |
| R (rstan) | 🔜 Planned |

---

## Citing This Tool

If you use BioAnchor in your research, please cite:

```
[Paper citation — in preparation]
```

And add to your Methods section:

> "MCMC analysis artifacts (manifest, posterior summary, and software environment)
> were permanently archived on the Arweave network using BioAnchor v0.1.0
> (TX ID: https://arweave.net/YOUR_TX_ID)."

---

## License

MIT License. See [LICENSE](LICENSE).
