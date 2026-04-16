"""
BioAnchor Manifest
==================
Standardized, minimal artifact format for permanently archiving
Bayesian/MCMC analysis metadata on Arweave.

Design principles:
  - Raw data NEVER uploaded (privacy + cost)
  - SHA-256 hash of input data is the link
  - Small enough to be human-readable (<10 KB target)
  - Deterministic: same inputs → same manifest
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BIOANCHOR_VERSION = "0.1.0"
MANIFEST_SCHEMA_VERSION = "1.0"


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class SoftwareEnv:
    language: str = field(default_factory=lambda: f"Python {sys.version.split()[0]}")
    platform: str = field(default_factory=platform.platform)
    packages: dict[str, str] = field(default_factory=dict)

    @classmethod
    def capture(cls, extra_packages: list[str] | None = None) -> "SoftwareEnv":
        """Auto-detect installed package versions."""
        import importlib.metadata as meta
        targets = ["numpy", "scipy", "pymc", "arviz", "cmdstanpy", "pandas"] + (extra_packages or [])
        pkgs = {}
        for pkg in targets:
            try:
                pkgs[pkg] = meta.version(pkg)
            except meta.PackageNotFoundError:
                pass
        return cls(packages=pkgs)


@dataclass
class DataArtifact:
    """Represents input data — only its hash, never the data itself."""
    sha256: str
    description: str
    n_samples: int | None = None
    n_features: int | None = None
    source: str | None = None  # e.g., "TCGA-BRCA", "GSE12345", "synthetic"

    @classmethod
    def from_array(cls, arr, description: str, source: str | None = None) -> "DataArtifact":
        import numpy as np
        a = np.asarray(arr)
        h = hashlib.sha256(a.tobytes()).hexdigest()
        shape = a.shape
        return cls(
            sha256=h,
            description=description,
            n_samples=shape[0] if len(shape) >= 1 else None,
            n_features=shape[1] if len(shape) >= 2 else None,
            source=source,
        )

    @classmethod
    def from_file(cls, path: str | Path, description: str, source: str | None = None) -> "DataArtifact":
        p = Path(path)
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        return cls(sha256=h, description=description, source=source)


@dataclass
class MCMCSummary:
    """
    Compact summary of MCMC run — reproducible without the full trace.
    Full trace is NOT uploaded; seed + prior_spec → full reproducibility.
    """
    sampler: str                          # NUTS, HMC, MH, SMC, ...
    n_chains: int
    n_draws: int
    n_warmup: int
    seed: int | list[int]
    prior_spec: dict[str, Any]            # {param_name: "dist(args)"}
    posterior_mean: dict[str, float]      # point estimates
    posterior_std: dict[str, float]
    r_hat: dict[str, float]               # convergence diagnostic
    ess_bulk: dict[str, float]            # effective sample size
    divergences: int = 0
    acceptance_rate: float | None = None

    @classmethod
    def from_arviz(cls, idata, sampler: str = "NUTS", seed: int | None = None) -> "MCMCSummary":
        """Build summary from an ArviZ InferenceData object."""
        import arviz as az
        import numpy as np

        summary = az.summary(idata, round_to=6)

        def _prior_spec_from_idata(idata) -> dict:
            """Extract prior info if available."""
            if hasattr(idata, "prior"):
                return {v: "see prior group" for v in idata.prior.data_vars}
            return {}

        divergences = 0
        if hasattr(idata, "sample_stats") and "diverging" in idata.sample_stats:
            divergences = int(idata.sample_stats.diverging.values.sum())

        acc_rate = None
        if hasattr(idata, "sample_stats") and "acceptance_rate" in idata.sample_stats:
            acc_rate = float(idata.sample_stats.acceptance_rate.values.mean())

        # Infer n_chains / n_draws
        posterior = idata.posterior
        chain_dim = posterior.dims.get("chain", None)
        draw_dim = posterior.dims.get("draw", None)
        n_chains = len(posterior.chain) if chain_dim else 1
        n_draws = len(posterior.draw) if draw_dim else 0

        warmup = 0
        if hasattr(idata, "warmup_posterior"):
            warmup = len(idata.warmup_posterior.draw)

        return cls(
            sampler=sampler,
            n_chains=n_chains,
            n_draws=n_draws,
            n_warmup=warmup,
            seed=seed if seed is not None else -1,
            prior_spec=_prior_spec_from_idata(idata),
            posterior_mean={k: float(v) for k, v in summary["mean"].items()},
            posterior_std={k: float(v) for k, v in summary["sd"].items()},
            r_hat={k: float(v) for k, v in summary["r_hat"].items()},
            ess_bulk={k: float(v) for k, v in summary["ess_bulk"].items()},
            divergences=divergences,
            acceptance_rate=acc_rate,
        )


@dataclass
class BioAnchorManifest:
    """
    Top-level manifest. This is what gets serialised to JSON and uploaded to Arweave.
    """
    # Identity
    schema_version: str = MANIFEST_SCHEMA_VERSION
    bioanchor_version: str = BIOANCHOR_VERSION
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Study metadata (free-form, user-supplied)
    title: str = ""
    description: str = ""
    authors: list[str] = field(default_factory=list)
    analysis_type: str = "MCMC"           # MCMC | VI | ABC | HMC | ...
    domain: str = ""                      # drug_discovery | genomics | clinical | ...
    tags: list[str] = field(default_factory=list)

    # Core components
    software: SoftwareEnv = field(default_factory=SoftwareEnv)
    data: DataArtifact | None = None
    mcmc: MCMCSummary | None = None

    # Filled after upload
    arweave_tx: str | None = None
    arweave_url: str | None = None

    # Optional: link to prior upload (chain of analyses)
    parent_tx: str | None = None

    # ── Serialisation ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return _clean(asdict(self))

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: str | Path) -> Path:
        p = Path(path)
        p.write_text(self.to_json())
        return p

    @classmethod
    def load(cls, path: str | Path) -> "BioAnchorManifest":
        raw = json.loads(Path(path).read_text())
        return _from_dict(cls, raw)

    # ── Fingerprint ──────────────────────────────────────────────────────────

    def fingerprint(self) -> str:
        """
        Deterministic SHA-256 of the manifest (excluding arweave_tx fields).
        Useful for verifying integrity after download.
        """
        d = self.to_dict()
        d.pop("arweave_tx", None)
        d.pop("arweave_url", None)
        canonical = json.dumps(d, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode()).hexdigest()

    # ── Display ──────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        tx = self.arweave_tx or "not uploaded"
        return (
            f"BioAnchorManifest(\n"
            f"  title='{self.title}'\n"
            f"  analysis={self.analysis_type} / {self.domain}\n"
            f"  created={self.created_at}\n"
            f"  arweave_tx={tx}\n"
            f")"
        )


# ── Helpers ──────────────────────────────────────────────────────────────────

def _clean(d: Any) -> Any:
    """Recursively remove None values from nested dicts."""
    if isinstance(d, dict):
        return {k: _clean(v) for k, v in d.items() if v is not None}
    if isinstance(d, list):
        return [_clean(i) for i in d]
    return d


def _from_dict(cls, d: dict):
    """Naive reconstruction — good enough for our flat-ish schema."""
    # Just return as a plain dict wrapper for now; full deserialisation TBD
    m = cls.__new__(cls)
    for f in cls.__dataclass_fields__:
        setattr(m, f, d.get(f, cls.__dataclass_fields__[f].default))
    return m
