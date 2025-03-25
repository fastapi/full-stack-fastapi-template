# config.py - Reading and writing Git config files
# Copyright (C) 2011-2013 Jelmer Vernooij <jelmer@jelmer.uk>
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

"""Working with Git submodules."""

from collections.abc import Iterator

from .object_store import iter_tree_contents
from .objects import S_ISGITLINK


def iter_cached_submodules(store, root_tree_id: bytes) -> Iterator[tuple[str, bytes]]:
    """Iterate over cached submodules.

    Args:
      store: Object store to iterate
      root_tree_id: SHA of root tree

    Returns:
      Iterator over over (path, sha) tuples
    """
    for entry in iter_tree_contents(store, root_tree_id):
        if S_ISGITLINK(entry.mode):
            yield entry.path, entry.sha
