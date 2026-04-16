"""
bioanchor CLI

Commands:
  bioanchor upload   --manifest manifest.json --wallet wallet.json
  bioanchor verify   <TX_ID>
  bioanchor fetch    <TX_ID>
  bioanchor balance  --wallet wallet.json
  bioanchor init     --output manifest_template.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def cmd_upload(args):
    from bioanchor.manifest import BioAnchorManifest
    from bioanchor.uploaders.arweave import ArweaveUploader, MockUploader

    manifest = BioAnchorManifest.load(args.manifest)

    if args.mock:
        uploader = MockUploader()
    else:
        if not args.wallet:
            print("Error: --wallet required (or use --mock for testing)")
            sys.exit(1)
        uploader = ArweaveUploader(args.wallet)

    print(f"Manifest size : {len(manifest.to_json()) / 1024:.2f} KB")
    print(f"Fingerprint   : {manifest.fingerprint()}")
    print()

    tx_id = uploader.upload(manifest)

    # Save updated manifest with TX ID
    out = Path(args.manifest)
    manifest.save(out)
    print(f"\nManifest updated with TX ID → {out}")


def cmd_verify(args):
    from bioanchor.uploaders.arweave import ArweaveUploader

    print(f"Verifying {args.tx_id} ...")
    report = ArweaveUploader.verify(args.tx_id)

    print(f"\n{'='*50}")
    print(f"TX ID       : {report['tx_id']}")
    print(f"Retrievable : {'✓' if report['retrievable'] else '✗'}")

    if report.get("checks"):
        print("\nChecks:")
        for k, v in report["checks"].items():
            icon = "✓" if v else "✗"
            print(f"  {icon}  {k}")

    if report.get("created_at"):
        print(f"\nCreated     : {report['created_at']}")

    print(f"\nResult      : {'PASSED ✓' if report.get('passed') else 'FAILED ✗'}")


def cmd_fetch(args):
    from bioanchor.uploaders.arweave import ArweaveUploader

    print(f"Fetching {args.tx_id} ...")
    data = ArweaveUploader.fetch(args.tx_id)
    print(json.dumps(data, indent=2))


def cmd_balance(args):
    from bioanchor.uploaders.arweave import ArweaveUploader

    uploader = ArweaveUploader(args.wallet)
    bal = uploader.balance()
    print(f"Wallet balance: {bal:.6f} AR")


def cmd_init(args):
    """Write a blank manifest template."""
    from bioanchor.manifest import BioAnchorManifest, DataArtifact, MCMCSummary, SoftwareEnv

    template = {
        "schema_version": "1.0",
        "bioanchor_version": "0.1.0",
        "title": "My MCMC Analysis",
        "description": "Bayesian model for ...",
        "authors": ["Name <email>"],
        "analysis_type": "MCMC",
        "domain": "drug_discovery",
        "tags": ["bayesian", "pymc"],
        "software": {
            "language": "Python 3.x",
            "packages": {"pymc": "5.x", "arviz": "0.x"}
        },
        "data": {
            "sha256": "<sha256 of your input data>",
            "description": "Dataset description",
            "n_samples": None,
            "n_features": None,
            "source": "e.g. TCGA-BRCA"
        },
        "mcmc": {
            "sampler": "NUTS",
            "n_chains": 4,
            "n_draws": 2000,
            "n_warmup": 1000,
            "seed": 42,
            "prior_spec": {"param_name": "Normal(0, 1)"},
            "posterior_mean": {},
            "posterior_std": {},
            "r_hat": {},
            "ess_bulk": {},
            "divergences": 0
        }
    }

    out = Path(args.output)
    out.write_text(json.dumps(template, indent=2))
    print(f"Template written to {out}")
    print("Fill in the fields and run: bioanchor upload --manifest <file> --wallet <wallet.json>")


def main():
    parser = argparse.ArgumentParser(
        prog="bioanchor",
        description="Permanently archive Bayesian/MCMC analysis artifacts on Arweave"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # upload
    p_upload = sub.add_parser("upload", help="Upload manifest to Arweave")
    p_upload.add_argument("--manifest", required=True, help="Path to manifest JSON")
    p_upload.add_argument("--wallet", help="Arweave wallet JWK JSON")
    p_upload.add_argument("--mock", action="store_true", help="Dry run (no real upload)")

    # verify
    p_verify = sub.add_parser("verify", help="Verify an uploaded manifest")
    p_verify.add_argument("tx_id", help="Arweave transaction ID")

    # fetch
    p_fetch = sub.add_parser("fetch", help="Fetch and print a manifest")
    p_fetch.add_argument("tx_id", help="Arweave transaction ID")

    # balance
    p_balance = sub.add_parser("balance", help="Check wallet AR balance")
    p_balance.add_argument("--wallet", required=True)

    # init
    p_init = sub.add_parser("init", help="Generate a manifest template")
    p_init.add_argument("--output", default="bioanchor_manifest.json")

    args = parser.parse_args()
    dispatch = {
        "upload": cmd_upload,
        "verify": cmd_verify,
        "fetch": cmd_fetch,
        "balance": cmd_balance,
        "init": cmd_init,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
