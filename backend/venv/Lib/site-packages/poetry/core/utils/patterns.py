from __future__ import annotations

import re


AUTHOR_REGEX = re.compile(r"(?u)^(?P<name>[^<>]+)(?: <(?P<email>.+?)>)?$")

wheel_file_re = re.compile(
    r"""^(?P<namever>(?P<name>.+?)(-(?P<ver>\d.+?))?)
        ((-(?P<build>\d.*?))?-(?P<pyver>.+?)-(?P<abi>.+?)-(?P<plat>.+?)
        \.whl|\.dist-info)$""",
    re.VERBOSE,
)
