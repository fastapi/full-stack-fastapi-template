# bundle.py -- Bundle format support
# Copyright (C) 2020 Jelmer Vernooij <jelmer@jelmer.uk>
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
# Dulwich is dual-licensed under the Apache License, Version 2.0 and the GNU
# General Public License as public by the Free Software Foundation; version 2.0
# or (at your option) any later version. You can redistribute it and/or
# modify it under the terms of either of these two licenses.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You should have received a copy of the licenses; if not, see
# <http://www.gnu.org/licenses/> for a copy of the GNU General Public License
# and <http://www.apache.org/licenses/LICENSE-2.0> for a copy of the Apache
# License, Version 2.0.
#

"""Bundle format support."""

from collections.abc import Sequence
from typing import Optional, Union

from .pack import PackData, write_pack_data


class Bundle:
    version: Optional[int]

    capabilities: dict[str, str]
    prerequisites: list[tuple[bytes, str]]
    references: dict[str, bytes]
    pack_data: Union[PackData, Sequence[bytes]]

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__}(version={self.version}, "
            f"capabilities={self.capabilities}, "
            f"prerequisites={self.prerequisites}, "
            f"references={self.references})>"
        )

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        if self.version != other.version:
            return False
        if self.capabilities != other.capabilities:
            return False
        if self.prerequisites != other.prerequisites:
            return False
        if self.references != other.references:
            return False
        if self.pack_data != other.pack_data:
            return False
        return True


def _read_bundle(f, version):
    capabilities = {}
    prerequisites = []
    references = {}
    line = f.readline()
    if version >= 3:
        while line.startswith(b"@"):
            line = line[1:].rstrip(b"\n")
            try:
                key, value = line.split(b"=", 1)
            except ValueError:
                key = line
                value = None
            else:
                value = value.decode("utf-8")
            capabilities[key.decode("utf-8")] = value
            line = f.readline()
    while line.startswith(b"-"):
        (obj_id, comment) = line[1:].rstrip(b"\n").split(b" ", 1)
        prerequisites.append((obj_id, comment.decode("utf-8")))
        line = f.readline()
    while line != b"\n":
        (obj_id, ref) = line.rstrip(b"\n").split(b" ", 1)
        references[ref] = obj_id
        line = f.readline()
    pack_data = PackData.from_file(f)
    ret = Bundle()
    ret.references = references
    ret.capabilities = capabilities
    ret.prerequisites = prerequisites
    ret.pack_data = pack_data
    ret.version = version
    return ret


def read_bundle(f):
    """Read a bundle file."""
    firstline = f.readline()
    if firstline == b"# v2 git bundle\n":
        return _read_bundle(f, 2)
    if firstline == b"# v3 git bundle\n":
        return _read_bundle(f, 3)
    raise AssertionError(f"unsupported bundle format header: {firstline!r}")


def write_bundle(f, bundle) -> None:
    version = bundle.version
    if version is None:
        if bundle.capabilities:
            version = 3
        else:
            version = 2
    if version == 2:
        f.write(b"# v2 git bundle\n")
    elif version == 3:
        f.write(b"# v3 git bundle\n")
    else:
        raise AssertionError(f"unknown version {version}")
    if version == 3:
        for key, value in bundle.capabilities.items():
            f.write(b"@" + key.encode("utf-8"))
            if value is not None:
                f.write(b"=" + value.encode("utf-8"))
            f.write(b"\n")
    for obj_id, comment in bundle.prerequisites:
        f.write(b"-%s %s\n" % (obj_id, comment.encode("utf-8")))
    for ref, obj_id in bundle.references.items():
        f.write(b"%s %s\n" % (obj_id, ref))
    f.write(b"\n")
    write_pack_data(
        f.write,
        num_records=len(bundle.pack_data),
        records=bundle.pack_data.iter_unpacked(),
    )
