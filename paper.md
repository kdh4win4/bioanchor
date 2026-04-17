---
title: 'BioAnchor: Permanent and Verifiable Archiving of Bayesian/MCMC Analysis Artifacts via Arweave'
tags:
  - Python
  - Bayesian inference
  - MCMC
  - reproducibility
  - Arweave
  - drug discovery
  - open science
authors:
  - name: Dohoon Kim
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Promptgenix LLC
    index: 1
date: 17 April 2026
bibliography: paper.bib
---

# Summary

Bayesian and Markov chain Monte Carlo (MCMC) analyses are foundational to
computational biology, yet the artifacts required for their reproduction —
prior specifications, random seeds, posterior summaries, and software
environments — are rarely preserved in an accessible, permanent form.
Existing repositories such as GitHub, Zenodo, and OSF provide no mathematical
guarantee against deletion or access restriction.

`BioAnchor` is a Python package that addresses this gap by archiving a
compact, standardized JSON manifest (<5 KB) of MCMC analysis metadata on
Arweave, a decentralized storage network with cryptographic permanence
guarantees. The resulting Arweave transaction ID (TX ID) can be embedded
directly in manuscripts, enabling any reader to verify convergence diagnostics
and reproduce analyses from seed — permanently and without authentication.

# Statement of Need

The reproducibility crisis in computational science is well documented
[@baker2016reproducibility; @peng2011reproducible; @sandve2013ten].
In Bayesian analyses specifically, three artifacts are jointly necessary
for reproduction: (i) the prior specification; (ii) the random seed;
and (iii) the exact software environment. These are rarely preserved
together [@wilkinson2016fair].

Existing solutions are partial. Code repositories capture software but
not executed state. Data repositories host outputs but lack structured
schemas for MCMC metadata. Container images preserve environments but
are large and may themselves become inaccessible. Critically, none of
these platforms provides a mathematical guarantee of permanence.

`BioAnchor` fills this gap with three contributions:

1. A **standardized manifest format** (schema v1.0) capturing posterior
   summaries, convergence diagnostics (R-hat [@vehtari2021rhat], ESS),
   prior specifications, and software environment in a single JSON document.

2. A **Python package** (`pip install bioanchor`) with native integration
   for PyMC [@abril2023pymc] and ArviZ [@kumar2019arviz], and a
   command-line interface for upload, verification, and wallet management.

3. **Arweave-backed permanence**: a one-time fee of approximately $0.0001
   per manifest funds storage for a minimum of 200 years [@williams2019arweave],
   providing a qualitatively different guarantee from existing repositories.

# Implementation

`BioAnchor` is implemented in Python (≥3.10) and distributed via PyPI
under the MIT license. The high-level API wraps the full archive workflow
in a single call:

```python
from bioanchor import BioAnchor

ba = BioAnchor(wallet_path="wallet.json")
tx_id = ba.archive_pymc(
    idata, model=model, seed=42,
    data=X, title="Bayesian IC50 estimation",
    authors=["Dohoon Kim"], domain="drug_discovery",
)
# → https://arweave.net/<tx_id>  (permanent)
```

Raw data are never uploaded — only the SHA-256 hash of the input array,
providing cryptographic proof of data identity without exposing private
or large datasets. The manifest is deterministic: identical analyses
produce identical fingerprints, enabling tamper detection.

# Case Study

We demonstrate `BioAnchor` on a four-parameter Hill equation dose-response
model for IC50 estimation, a standard pharmacokinetic task [@sebaugh2011ic50].
Twelve simulated concentration-response measurements were fitted using
PyMC 5.28.4 with the NUTS sampler (2 chains, 1,000 draws, seed = 42).
Posterior estimates accurately recovered true parameters (IC50 = 0.465 μM,
SD = 0.022; true: 0.500 μM), with all R-hat ≤ 1.002 and bulk ESS ≥ 1,352,
indicating excellent convergence.

The complete manifest (2.1 KB) was archived on Arweave. The permanent URL is:

> https://arweave.net/2lIZtjsu120ERqPKu6XbITpUnAveWeH7hI4owBfNCdY

This URL is publicly accessible without authentication and will remain so
indefinitely, satisfying the FAIR principles requirement for persistent
identifiers [@wilkinson2016fair].

# Acknowledgements

No external funding was received for this work.

# References
