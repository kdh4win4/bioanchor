"""
example_drug_discovery.py
=========================
End-to-end example: Bayesian dose-response model → BioAnchor archive.

Simulates a typical drug discovery scenario:
  - Compound potency estimation (IC50)
  - Hill equation with Bayesian priors
  - MCMC via PyMC
  - Archive to Arweave (mock mode, no wallet needed)

Run:
    python examples/example_drug_discovery.py
"""

import sys
sys.path.insert(0, "..")  # run from examples/ or project root

import numpy as np

# ── Simulate dose-response data ───────────────────────────────────────────────

print("=" * 60)
print("BioAnchor — Drug Discovery Example")
print("Bayesian dose-response (Hill equation) model")
print("=" * 60)
print()

np.random.seed(42)
n_conc = 12
log_conc = np.linspace(-3, 2, n_conc)          # log10(concentration in μM)
conc = 10 ** log_conc

# True parameters
true_ic50   = 0.5    # μM
true_hill   = 1.8
true_bottom = 2.0    # % activity
true_top    = 98.0

# Hill equation
def hill(c, ic50, n, bottom, top):
    return bottom + (top - bottom) / (1 + (ic50 / c) ** n)

y_true = hill(conc, true_ic50, true_hill, true_bottom, true_top)
y_obs  = y_true + np.random.normal(0, 3.0, size=n_conc)
y_obs  = np.clip(y_obs, 0, 100)

print(f"Simulated {n_conc} concentration points")
print(f"True IC50 = {true_ic50} μM, Hill = {true_hill}")
print()

# ── PyMC model ────────────────────────────────────────────────────────────────

try:
    import pymc as pm
    import arviz as az

    print("Building PyMC model...")

    with pm.Model() as dose_response_model:
        # Priors
        log_ic50 = pm.Normal("log_ic50", mu=-0.3, sigma=1.0)   # log10(IC50) prior
        ic50     = pm.Deterministic("ic50", 10 ** log_ic50)
        hill_n   = pm.HalfNormal("hill_n", sigma=2.0)
        bottom   = pm.Normal("bottom", mu=0, sigma=10)
        top      = pm.Normal("top", mu=100, sigma=10)
        sigma    = pm.HalfNormal("sigma", sigma=5)

        # Likelihood
        mu = bottom + (top - bottom) / (1 + (ic50 / conc) ** hill_n)
        obs = pm.Normal("obs", mu=mu, sigma=sigma, observed=y_obs)

        # Sample
        print("Sampling... (this may take ~30s)")
        idata = pm.sample(
            draws=1000,
            tune=500,
            chains=2,
            random_seed=42,
            progressbar=True,
            target_accept=0.9,
        )

    print()
    print("Sampling complete.")
    summary = az.summary(idata, var_names=["log_ic50", "ic50", "hill_n"])
    print(summary.to_string())
    print()

    # ── Archive with BioAnchor ────────────────────────────────────────────────

    from bioanchor import BioAnchor

    ba = BioAnchor(mock=True)  # swap mock=False + wallet_path="wallet.json" for real upload

    tx_id = ba.archive_pymc(
        idata=idata,
        model=dose_response_model,
        seed=42,
        data=np.column_stack([log_conc, y_obs]),
        data_description="Synthetic dose-response: 12-point IC50 curve (log10 μM, % activity)",
        data_source="synthetic",
        title="Bayesian dose-response (Hill equation) — IC50 estimation",
        description=(
            "Four-parameter Hill equation fitted via NUTS to simulated dose-response data. "
            "Demonstrates BioAnchor archival of drug discovery MCMC results."
        ),
        authors=["BioAnchor Example"],
        domain="drug_discovery",
        tags=["dose-response", "ic50", "hill-equation", "pymc", "nuts"],
        save_manifest="bioanchor_manifest_example.json",
    )

    print()
    print("Archive complete!")
    print(f"TX ID : {tx_id}")
    print(f"URL   : https://arweave.net/{tx_id}")
    print()
    print("Manifest saved to: bioanchor_manifest_example.json")

except ImportError as e:
    print(f"PyMC not installed ({e}), running manifest-only demo...")

    # ── Manifest-only demo (no PyMC needed) ──────────────────────────────────

    from bioanchor.manifest import (
        BioAnchorManifest, DataArtifact, MCMCSummary, SoftwareEnv
    )
    from bioanchor.uploaders.arweave import MockUploader

    data_artifact = DataArtifact.from_array(
        np.column_stack([log_conc, y_obs]),
        description="Synthetic dose-response: 12-point IC50 curve",
        source="synthetic",
    )

    mcmc_summary = MCMCSummary(
        sampler="NUTS",
        n_chains=2,
        n_draws=1000,
        n_warmup=500,
        seed=42,
        prior_spec={
            "log_ic50": "Normal(mu=-0.3, sigma=1.0)",
            "hill_n":   "HalfNormal(sigma=2.0)",
            "bottom":   "Normal(mu=0, sigma=10)",
            "top":      "Normal(mu=100, sigma=10)",
            "sigma":    "HalfNormal(sigma=5)",
        },
        posterior_mean={"log_ic50": -0.31, "ic50": 0.49, "hill_n": 1.79},
        posterior_std={"log_ic50": 0.09, "ic50": 0.10, "hill_n": 0.21},
        r_hat={"log_ic50": 1.001, "ic50": 1.001, "hill_n": 1.003},
        ess_bulk={"log_ic50": 892.0, "ic50": 887.0, "hill_n": 755.0},
        divergences=0,
        acceptance_rate=0.93,
    )

    manifest = BioAnchorManifest(
        title="Bayesian dose-response (Hill equation) — IC50 estimation",
        authors=["BioAnchor Example"],
        analysis_type="MCMC",
        domain="drug_discovery",
        tags=["dose-response", "ic50", "hill-equation", "nuts"],
        software=SoftwareEnv.capture(),
        data=data_artifact,
        mcmc=mcmc_summary,
    )

    print("Manifest fingerprint:", manifest.fingerprint())
    manifest.save("bioanchor_manifest_example.json")
    print("Manifest saved to: bioanchor_manifest_example.json")
    print()
    print("Manifest JSON (first 800 chars):")
    print(manifest.to_json()[:800], "...")

    # Mock upload
    uploader = MockUploader()
    tx_id = uploader.upload(manifest)
    print()
    print(f"Mock TX ID : {tx_id}")
    print(f"URL        : https://arweave.net/{tx_id}")
