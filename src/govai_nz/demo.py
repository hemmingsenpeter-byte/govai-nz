"""Run without network access, API keys, or real personal information."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .adapters import MockProvider, SQLiteAuditStore, UnavailableProvider
from .core import Classification, Gateway, PublicOnlyPolicy, Request


def main() -> None:
    with TemporaryDirectory(prefix="govai-nz-demo-") as directory:
        audit = SQLiteAuditStore(Path(directory) / "audit.sqlite")
        gateway = Gateway(MockProvider(), PublicOnlyPolicy(), audit)
        scenarios = [
            ("public", Request("Summarise a synthetic public document.", Classification.PUBLIC)),
            ("non-public", Request("Synthetic non-public material.", Classification.NON_PUBLIC)),
            ("human review", Request("Synthetic high-impact request.", Classification.PUBLIC, high_impact=True)),
        ]
        try:
            for name, request in scenarios:
                result = gateway.run(request)
                print(f"{name}: {result.status}")
            unavailable = Gateway(UnavailableProvider(), PublicOnlyPolicy(), audit)
            print(f"provider failure: {unavailable.run(scenarios[0][1]).status}")
            print("Audit events (metadata only; temporary database):")
            print(json.dumps(audit.export(), indent=2))
        finally:
            audit.close()


if __name__ == "__main__":
    main()
