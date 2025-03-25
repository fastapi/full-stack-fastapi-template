from __future__ import annotations

import re

from packaging.version import VERSION_PATTERN


COMPLETE_VERSION = re.compile(VERSION_PATTERN, re.VERBOSE | re.IGNORECASE)

CARET_CONSTRAINT = re.compile(
    rf"^\^\s*(?P<version>{VERSION_PATTERN})$", re.VERBOSE | re.IGNORECASE
)
TILDE_CONSTRAINT = re.compile(
    rf"^~(?!=)\s*(?P<version>{VERSION_PATTERN})$", re.VERBOSE | re.IGNORECASE
)
TILDE_PEP440_CONSTRAINT = re.compile(
    rf"^~=\s*(?P<version>{VERSION_PATTERN})$", re.VERBOSE | re.IGNORECASE
)
X_CONSTRAINT = re.compile(
    r"^(?P<op>!=|==)?\s*v?(?P<version>(\d+)(?:\.(\d+))?(?:\.(\d+))?)(?:\.\*)+$"
)

# note that we also allow technically incorrect version patterns with astrix (eg: 3.5.*)
# as this is supported by pip and appears in metadata within python packages
BASIC_CONSTRAINT = re.compile(
    rf"^(?P<op><>|!=|>=?|<=?|==?)?\s*(?P<version>{VERSION_PATTERN}|dev)(?P<wildcard>\.\*)?$",
    re.VERBOSE | re.IGNORECASE,
)

RELEASE_PATTERN = r"""
(?P<release>[0-9]+(?:\.[0-9]+)*)
(?:(\+|-)(?P<build>
    [0-9a-zA-Z-]+
    (?:\.[0-9a-zA-Z-]+)*
))?
"""

# pattern for non Python versions such as OS versions in `platform_release`
BASIC_RELEASE_CONSTRAINT = re.compile(
    rf"^(?P<op><>|!=|>=?|<=?|==?)?\s*(?P<version>{RELEASE_PATTERN})$",
    re.VERBOSE | re.IGNORECASE,
)
