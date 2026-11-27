"""The old path of PCM's Agent E2 client, kept for one step of a contract move (R-REPO-008, PCM D-133).

GENERATED. Do not edit by hand (D-070).

The client is pcm/core/agent_e2.py. The contract check C3 in private-cloud-workspace (checks/agent_e2_api.py,
load_pcm_client) loads it from this path as a standalone file. The move has three steps: (1) the client answers at
both paths, (2) C3 loads the new path, (3) this file and the build folder are removed.

This file loads the client from its new path as a standalone file, without importing any package, and takes over
every name it defines, so a caller reads the same functions here as there.
"""
import importlib.util as _util
from pathlib import Path as _Path

_PATH = _Path(__file__).resolve().parents[2] / "pcm" / "core" / "agent_e2.py"
_spec = _util.spec_from_file_location("pcm_agent_e2_client", _PATH)
_client = _util.module_from_spec(_spec)
_spec.loader.exec_module(_client)
globals().update({k: v for k, v in vars(_client).items() if not (k.startswith("__") and k.endswith("__"))})
