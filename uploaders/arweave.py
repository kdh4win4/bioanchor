"""
Arweave uploader for BioAnchor manifests.

Uses arweave-python-client under the hood.
Wallet is a standard Arweave JWK JSON file.

Install:  pip install arweave-python-client
Testnet:  set gateway="https://arweave.net" for mainnet,
          or use bundlr/irys for cheaper uploads.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bioanchor.manifest import BioAnchorManifest


ARWEAVE_GATEWAY = "https://arweave.net"


class ArweaveUploader:
    """
    Uploads a BioAnchorManifest JSON to Arweave.

    Parameters
    ----------
    wallet_path : str | Path
        Path to your Arweave JWK wallet JSON file.
        Generate one at https://arweave.app or via arweave-python-client.
    gateway : str
        Arweave gateway URL. Default: mainnet.
    """

    def __init__(self, wallet_path: str | Path, gateway: str = ARWEAVE_GATEWAY):
        self.gateway = gateway.rstrip("/")
        self.wallet_path = Path(wallet_path)
        self._wallet = None

    def _load_wallet(self):
        if self._wallet is None:
            try:
                import arweave
            except ImportError:
                raise ImportError(
                    "arweave-python-client not installed.\n"
                    "Run: pip install arweave-python-client"
                )
            self._wallet = arweave.Wallet(str(self.wallet_path))
        return self._wallet

    def balance(self) -> float:
        """Return wallet balance in AR."""
        w = self._load_wallet()
        return float(w.balance)

    def upload(self, manifest: "BioAnchorManifest") -> str:
        """
        Upload manifest to Arweave.
        Returns the transaction ID (TX ID).
        Modifies manifest.arweave_tx and manifest.arweave_url in-place.
        """
        import arweave

        wallet = self._load_wallet()
        payload = manifest.to_json()

        tx = arweave.Transaction(wallet, data=payload)
        def ascii_safe(s):
            return str(s).encode("ascii", "ignore").decode()

        tx.add_tag("Content-Type", "application/json")
        tx.add_tag("App-Name", ascii_safe("BioAnchor"))
        tx.add_tag("App-Version", ascii_safe(manifest.bioanchor_version))
        tx.add_tag("Schema-Version", ascii_safe(manifest.schema_version))
        tx.add_tag("Analysis-Type", ascii_safe(manifest.analysis_type))
        tx.add_tag("Domain", ascii_safe(manifest.domain or ""))
        tx.add_tag("Created-At", ascii_safe(manifest.created_at))
        if manifest.title:
            tx.add_tag("Title", ascii_safe(manifest.title))
        for tag in manifest.tags:
            tx.add_tag("Tag", ascii_safe(tag))

        tx.sign()
        tx.send()

        manifest.arweave_tx = tx.id
        manifest.arweave_url = f"{self.gateway}/{tx.id}"

        return tx.id

    @staticmethod
    def fetch(tx_id: str, gateway: str = ARWEAVE_GATEWAY) -> dict:
        """Download and parse a manifest by TX ID."""
        import urllib.request
        url = f"{gateway.rstrip('/')}/{tx_id}"
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read())

    @staticmethod
    def verify(tx_id: str, gateway: str = ARWEAVE_GATEWAY) -> dict:
        """
        Fetch manifest and return a verification report.
        Checks: retrievable, schema version, fingerprint consistency.
        """
        import urllib.request
        from bioanchor.manifest import BioAnchorManifest

        report = {"tx_id": tx_id, "retrievable": False, "checks": {}}

        url = f"{gateway.rstrip('/')}/{tx_id}"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                raw = json.loads(r.read())
            report["retrievable"] = True
        except Exception as e:
            report["error"] = str(e)
            return report

        report["checks"]["schema_version"] = raw.get("schema_version") == "1.0"
        report["checks"]["has_mcmc"] = "mcmc" in raw
        report["checks"]["has_data_hash"] = bool(raw.get("data", {}).get("sha256"))
        report["checks"]["has_seed"] = raw.get("mcmc", {}).get("seed", -1) != -1
        report["checks"]["r_hat_ok"] = all(
            v < 1.05 for v in raw.get("mcmc", {}).get("r_hat", {}).values()
        )
        report["summary"] = raw.get("mcmc", {}).get("posterior_mean", {})
        report["created_at"] = raw.get("created_at")
        report["passed"] = all(report["checks"].values())

        return report


class MockUploader:
    """
    Drop-in replacement for ArweaveUploader that doesn't require
    a real wallet. Useful for development and testing.
    Returns a fake TX ID.
    """

    def __init__(self, *args, **kwargs):
        import hashlib, random
        self._rng = random.Random(42)

    def balance(self) -> float:
        return 999.0

    def upload(self, manifest: "BioAnchorManifest") -> str:
        import hashlib, random
        fake_tx = hashlib.sha256(
            (manifest.to_json() + str(time.time())).encode()
        ).hexdigest()[:43]
        manifest.arweave_tx = fake_tx
        manifest.arweave_url = f"https://arweave.net/{fake_tx}"
        print(f"[MockUploader] Fake TX: {fake_tx}")
        return fake_tx

    @staticmethod
    def fetch(tx_id: str, **kwargs) -> dict:
        return {"mock": True, "tx_id": tx_id}

    @staticmethod
    def verify(tx_id: str, **kwargs) -> dict:
        return {"mock": True, "tx_id": tx_id, "passed": True}
