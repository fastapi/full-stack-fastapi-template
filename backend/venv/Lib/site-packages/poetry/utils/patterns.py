from __future__ import annotations

import re


wheel_file_re = re.compile(
    r"^(?P<namever>(?P<name>.+?)-(?P<ver>\d[^-]*))"
    r"(-(?P<build>\d[^-]*))?"
    r"-(?P<pyver>[^-]+)"
    r"-(?P<abi>[^-]+)"
    r"-(?P<plat>[^-]+)"
    r"\.whl$",
    re.VERBOSE,
)

sdist_file_re = re.compile(
    r"^(?P<namever>(?P<name>.+?)-(?P<ver>\d[^-]*?))"
    r"(\.sdist)?\.(?P<format>(zip|tar(\.(gz|bz2|xz|Z))?))$"
)
