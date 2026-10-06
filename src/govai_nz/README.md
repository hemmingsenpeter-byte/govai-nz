# Shared Python foundation

**Status:** Foundation exists; expansion planned.

Current runtime demo is core.py, adapters.py and demo.py. New shared contracts/types/helpers belong here. The versioned wire bundle is `contracts.v1.schema.json`; Python contract classes provide strict dictionary serialization. Extract service/provider implementations to canonical top-level boundaries only in a reviewed migration with imports/tests updated.

Before writing files, read the [repository map](../../REPOSITORY_MAP.md), CONTRIBUTING.md and this directory's scope. Add implementation-specific commands, contracts and test locations when this module becomes executable.
