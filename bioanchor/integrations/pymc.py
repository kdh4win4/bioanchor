"""
PyMC integration for BioAnchor.

Usage
-----
    import pymc as pm
    from bioanchor.integrations.pymc import archive_pymc

    with pm.Model() as model:
        alpha = pm.Normal("alpha", 0, 1)
        ...
        idata = pm.sample(2000, random_seed=42)

    tx_id = archive_pymc(
        idata=idata,
        model=model,
        seed=42,
        data=X,
        data_description="TCGA-BRCA expression (n=500, p=200)",
        title="Bayesian sparse regression — drug target identification",
        authors=["Your Name"],
        domain="drug_discovery",
        wallet_path="wallet.json",
    )
    print(f"https://arweave.net/{tx_id}")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bioanchor.manifest import (
    BioAnchorManifest,
    DataArtifact,
    MCMCSummary,
    SoftwareEnv,
)


def archive_pymc(
    idata,
    model=None,
    seed: int | None = None,
    data=None,
    data_description: str = "",
    data_source: str | None = None,
    title: str = "",
    description: str = "",
    authors: list[str] | None = None,
    domain: str = "",
    tags: list[str] | None = None,
    wallet_path: str | Path | None = None,
    mock: bool = False,
    save_manifest: str | Path | None = None,
) -> str:
    """
    One-shot: build manifest from PyMC InferenceData and upload to Arweave.

    Parameters
    ----------
    idata       : ArviZ InferenceData from pm.sample()
    model       : pm.Model (optional, for prior extraction)
    seed        : random_seed used in pm.sample()
    data        : numpy array or file path — used only for hashing
    wallet_path : path to Arweave JWK wallet JSON
    mock        : if True, use MockUploader (no real wallet needed)
    save_manifest : if set, save manifest JSON to this path

    Returns
    -------
    str : Arweave TX ID
    """
    # ── Build sub-components ──────────────────────────────────────────────

    software = SoftwareEnv.capture(extra_packages=["pymc", "arviz"])

    data_artifact = None
    if data is not None:
        if isinstance(data, (str, Path)):
            data_artifact = DataArtifact.from_file(
                data, description=data_description, source=data_source
            )
        else:
            import numpy as np
            data_artifact = DataArtifact.from_array(
                data, description=data_description, source=data_source
            )

    mcmc_summary = MCMCSummary.from_arviz(idata, sampler="NUTS", seed=seed)

    # Try to extract prior spec from model if provided
    if model is not None:
        try:
            prior_spec = _extract_prior_spec(model)
            mcmc_summary.prior_spec = prior_spec
        except Exception:
            pass  # Don't fail the whole upload for this

    # ── Assemble manifest ──────────────────────────────────────────────────

    manifest = BioAnchorManifest(
        title=title,
        description=description,
        authors=authors or [],
        analysis_type="MCMC",
        domain=domain,
        tags=tags or [],
        software=software,
        data=data_artifact,
        mcmc=mcmc_summary,
    )

    if save_manifest:
        manifest.save(save_manifest)
        print(f"Manifest saved to {save_manifest}")

    # ── Upload ─────────────────────────────────────────────────────────────

    if mock or wallet_path is None:
        from bioanchor.uploaders.arweave import MockUploader
        uploader = MockUploader()
    else:
        from bioanchor.uploaders.arweave import ArweaveUploader
        uploader = ArweaveUploader(wallet_path)

    print(f"Uploading to Arweave... ({len(manifest.to_json())/1024:.1f} KB)")
    tx_id = uploader.upload(manifest)
    print(f"✓ TX ID : {tx_id}")
    print(f"✓ URL   : https://arweave.net/{tx_id}")
    print()
    print("Add to your paper:")
    print(f'  "Analysis artifacts permanently archived at https://arweave.net/{tx_id}"')

    return tx_id


def _extract_prior_spec(model) -> dict[str, str]:
    """
    Extract human-readable prior descriptions from a PyMC model.
    e.g. {"alpha": "Normal(mu=0, sigma=1)", "beta": "HalfNormal(sigma=1)"}
    """
    spec = {}
    try:
        for rv in model.free_RVs:
            name = rv.name
            dist = rv.owner.op
            spec[name] = type(dist).__name__
    except Exception:
        pass
    return spec
