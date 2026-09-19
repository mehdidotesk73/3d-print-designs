"""Force cadgen's snapshot renderer onto the pre-installed Chromium binary.

This sandbox's Playwright pip package (1.63.0) expects browser revision 1243,
but only revision 1194 is pre-installed, and downloading 1243 is blocked by
this environment's egress policy. Chromium itself is fine for headless
screenshot rendering across that gap, so patch executable_path onto the
launch call instead of fetching a new browser.

Usage (from the project root): python3 scripts/snapshot_shim.py step snapshot
STEP/canister_back.step tmp/back.png -- same arguments as `cadgen`.
"""

import os
import sys

os.environ["CADGEN_DAEMON"] = "0"  # run in this process so the patch below applies

CHROMIUM_PATH = "/opt/pw-browsers/chromium"

from playwright.async_api import BrowserType  # noqa: E402

_orig_launch = BrowserType.launch


async def _patched_launch(self, **kwargs):
    kwargs.setdefault("executable_path", CHROMIUM_PATH)
    return await _orig_launch(self, **kwargs)


BrowserType.launch = _patched_launch

from cadgen.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
