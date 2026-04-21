"""
TurboUploader: BioAnchor uploader using ArDrive Turbo Python SDK.
Requires: pip install turbo-sdk
"""
import json
from typing import Optional

class TurboUploader:
    """
    Upload BioAnchor manifests to Arweave via ArDrive Turbo SDK.
    
    Advantages over raw ArweaveUploader:
    - Faster finality (Turbo bundling service)
    - ANS-104 data items (AR.IO compatible)
    - Credit-based payment (no per-TX wallet signing cost)
    
    Usage:
        uploader = TurboUploader(wallet_path="wallet.json")
        tx_id = uploader.upload(manifest_dict)
    """
    def __init__(
        self,
        wallet_path: Optional[str] = None,
        wallet_jwk: Optional[dict] = None,
        network: str = "mainnet",
    ):
        try:
            from turbo_sdk import Turbo, ArweaveSigner
        except ImportError:
            raise ImportError(
                "turbo-sdk is required for TurboUploader.\n"
                "Install with: pip install turbo-sdk"
            )
        if wallet_path is not None:
            with open(wallet_path, "r") as f:
                jwk = json.load(f)
        elif wallet_jwk is not None:
            jwk = wallet_jwk
        else:
            raise ValueError("Either wallet_path or wallet_jwk must be provided.")
        signer = ArweaveSigner(jwk)
        self.turbo = Turbo(signer, network=network)
        self.network = network

    def upload(self, manifest: dict) -> str:
        data = json.dumps(manifest, indent=2).encode("utf-8")
        tags = [
            {"name": "Content-Type",  "value": "application/json"},
            {"name": "App-Name",      "value": "BioAnchor"},
            {"name": "App-Version",   "value": manifest.get("bioanchor_version", "0.1.0")},
            {"name": "BioAnchor-Type","value": "mcmc-manifest"},
            {"name": "Model-Name",    "value": manifest.get("model_name", "unknown")},
            {"name": "Sampler",       "value": manifest.get("sampler", "unknown")},
            {"name": "Upload-Via",    "value": "turbo-sdk"},
        ]
        if doi := manifest.get("doi"):
            tags.append({"name": "DOI", "value": doi})
        result = self.turbo.upload(data, tags=tags)
        return result.id

    def get_balance(self) -> dict:
        balance = self.turbo.get_balance()
        return {"winc": balance, "network": self.network}
