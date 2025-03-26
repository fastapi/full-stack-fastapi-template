from __future__ import annotations

from collections import namedtuple
from typing import ClassVar


class License(namedtuple("License", "id name is_osi_approved is_deprecated")):
    id: str
    name: str
    is_osi_approved: bool
    is_deprecated: bool

    CLASSIFIER_SUPPORTED: ClassVar[set[str]] = {
        # Not OSI Approved
        "Aladdin",
        "CC0-1.0",
        "CECILL-B",
        "CECILL-C",
        "NPL-1.0",
        "NPL-1.1",
        # OSI Approved
        "AFPL",
        "AFL-1.1",
        "AFL-1.2",
        "AFL-2.0",
        "AFL-2.1",
        "AFL-3.0",
        "Apache-1.1",
        "Apache-2.0",
        "APSL-1.1",
        "APSL-1.2",
        "APSL-2.0",
        "Artistic-1.0",
        "Artistic-2.0",
        "AAL",
        "AGPL-3.0",
        "AGPL-3.0-only",
        "AGPL-3.0-or-later",
        "BSL-1.0",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "CDDL-1.0",
        "CECILL-2.1",
        "CPL-1.0",
        "EFL-1.0",
        "EFL-2.0",
        "EPL-1.0",
        "EPL-2.0",
        "EUPL-1.1",
        "EUPL-1.2",
        "GPL-2.0",
        "GPL-2.0+",
        "GPL-2.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0",
        "GPL-3.0+",
        "GPL-3.0-only",
        "GPL-3.0-or-later",
        "LGPL-2.0",
        "LGPL-2.0+",
        "LGPL-2.0-only",
        "LGPL-2.0-or-later",
        "LGPL-3.0",
        "LGPL-3.0+",
        "LGPL-3.0-only",
        "LGPL-3.0-or-later",
        "MIT",
        "MPL-1.0",
        "MPL-1.1",
        "MPL-1.2",
        "Nokia",
        "W3C",
        "ZPL-1.0",
        "ZPL-2.0",
        "ZPL-2.1",
    }

    CLASSIFIER_NAMES: ClassVar[dict[str, str]] = {
        # Not OSI Approved
        "Aladdin": "Aladdin Free Public License (AFPL)",
        "AFPL": "Aladdin Free Public License (AFPL)",
        "CC0-1.0": "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "CECILL-B": "CeCILL-B Free Software License Agreement (CECILL-B)",
        "CECILL-C": "CeCILL-C Free Software License Agreement (CECILL-C)",
        "NPL-1.0": "Netscape Public License (NPL)",
        "NPL-1.1": "Netscape Public License (NPL)",
        # OSI Approved
        "AFL-1.1": "Academic Free License (AFL)",
        "AFL-1.2": "Academic Free License (AFL)",
        "AFL-2.0": "Academic Free License (AFL)",
        "AFL-2.1": "Academic Free License (AFL)",
        "AFL-3.0": "Academic Free License (AFL)",
        "Apache-1.1": "Apache Software License",
        "Apache-2.0": "Apache Software License",
        "APSL-1.1": "Apple Public Source License",
        "APSL-1.2": "Apple Public Source License",
        "APSL-2.0": "Apple Public Source License",
        "Artistic-1.0": "Artistic License",
        "Artistic-2.0": "Artistic License",
        "AAL": "Attribution Assurance License",
        "AGPL-3.0": "GNU Affero General Public License v3",
        "AGPL-3.0-only": "GNU Affero General Public License v3",
        "AGPL-3.0-or-later": "GNU Affero General Public License v3 or later (AGPLv3+)",
        "BSL-1.0": "Boost Software License 1.0 (BSL-1.0)",
        "BSD-2-Clause": "BSD License",
        "BSD-3-Clause": "BSD License",
        "CDDL-1.0": "Common Development and Distribution License 1.0 (CDDL-1.0)",
        "CECILL-2.1": "CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)",
        "CPL-1.0": "Common Public License",
        "EPL-1.0": "Eclipse Public License 1.0 (EPL-1.0)",
        "EPL-2.0": "Eclipse Public License 2.0 (EPL-2.0)",
        "EFL-1.0": "Eiffel Forum License",
        "EFL-2.0": "Eiffel Forum License",
        "EUPL-1.1": "European Union Public Licence 1.1 (EUPL 1.1)",
        "EUPL-1.2": "European Union Public Licence 1.2 (EUPL 1.2)",
        "GPL-2.0": "GNU General Public License v2 (GPLv2)",
        "GPL-2.0-only": "GNU General Public License v2 (GPLv2)",
        "GPL-2.0+": "GNU General Public License v2 or later (GPLv2+)",
        "GPL-2.0-or-later": "GNU General Public License v2 or later (GPLv2+)",
        "GPL-3.0": "GNU General Public License v3 (GPLv3)",
        "GPL-3.0-only": "GNU General Public License v3 (GPLv3)",
        "GPL-3.0+": "GNU General Public License v3 or later (GPLv3+)",
        "GPL-3.0-or-later": "GNU General Public License v3 or later (GPLv3+)",
        "LGPL-2.0": "GNU Lesser General Public License v2 (LGPLv2)",
        "LGPL-2.0-only": "GNU Lesser General Public License v2 (LGPLv2)",
        "LGPL-2.0+": "GNU Lesser General Public License v2 or later (LGPLv2+)",
        "LGPL-2.0-or-later": "GNU Lesser General Public License v2 or later (LGPLv2+)",
        "LGPL-3.0": "GNU Lesser General Public License v3 (LGPLv3)",
        "LGPL-3.0-only": "GNU Lesser General Public License v3 (LGPLv3)",
        "LGPL-3.0+": "GNU Lesser General Public License v3 or later (LGPLv3+)",
        "LGPL-3.0-or-later": "GNU Lesser General Public License v3 or later (LGPLv3+)",
        "MPL-1.0": "Mozilla Public License 1.0 (MPL)",
        "MPL-1.1": "Mozilla Public License 1.1 (MPL 1.1)",
        "MPL-2.0": "Mozilla Public License 2.0 (MPL 2.0)",
        "W3C": "W3C License",
        "ZPL-1.1": "Zope Public License",
        "ZPL-2.0": "Zope Public License",
        "ZPL-2.1": "Zope Public License",
    }

    @property
    def classifier(self) -> str:
        parts = ["License"]

        if self.is_osi_approved:
            parts.append("OSI Approved")

        name = self.classifier_name
        if name is not None:
            parts.append(name)

        return " :: ".join(parts)

    @property
    def classifier_name(self) -> str | None:
        if self.id not in self.CLASSIFIER_SUPPORTED:
            if self.is_osi_approved:
                return None

            return "Other/Proprietary License"

        if self.id in self.CLASSIFIER_NAMES:
            return self.CLASSIFIER_NAMES[self.id]

        return self.name
