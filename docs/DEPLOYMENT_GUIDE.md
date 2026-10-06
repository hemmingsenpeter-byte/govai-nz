# Deployment guide

## Working local foundation

From repository root, with Python 3.12 or newer:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m govai_nz.demo
```

No API key, external model or persistent database is required. This runs a command-line demonstration; it does not start an HTTP service.

## Planned deployment areas

`infrastructure/local/` will contain local Compose/container examples after the first real service exists. `infrastructure/azure/` and `infrastructure/aws/` reserve provider-specific deployment boundaries; they currently contain placement guidance only.

Do not expose the foundation to real users or upload real agency records. Before deployment, document verified identity, configured controls, network/data destinations, secret provisioning, access boundaries, audit retention, recovery, operational ownership and independent review. Keep secrets and state outside Git.
