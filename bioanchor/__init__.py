from bioanchor.manifest import BioAnchorManifest, DataArtifact, MCMCSummary, SoftwareEnv

__version__ = "0.1.0"

class BioAnchor:
    def __init__(self, wallet_path=None, mock=False):
        self.wallet_path = wallet_path
        self.mock = mock or (wallet_path is None)

    def archive_pymc(self, idata, **kwargs):
        from bioanchor.integrations.pymc import archive_pymc
        kwargs.setdefault("mock", self.mock)
        kwargs.setdefault("wallet_path", self.wallet_path)
        return archive_pymc(idata, **kwargs)
