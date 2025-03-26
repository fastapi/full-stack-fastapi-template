# lfs.py -- Implementation of the LFS
# Copyright (C) 2020 Jelmer Vernooij
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

import hashlib
import os
import tempfile


class LFSStore:
    """Stores objects on disk, indexed by SHA256."""

    def __init__(self, path) -> None:
        self.path = path

    @classmethod
    def create(cls, lfs_dir):
        if not os.path.isdir(lfs_dir):
            os.mkdir(lfs_dir)
        os.mkdir(os.path.join(lfs_dir, "tmp"))
        os.mkdir(os.path.join(lfs_dir, "objects"))
        return cls(lfs_dir)

    @classmethod
    def from_repo(cls, repo, create=False):
        lfs_dir = os.path.join(repo.controldir, "lfs")
        if create:
            return cls.create(lfs_dir)
        return cls(lfs_dir)

    def _sha_path(self, sha):
        return os.path.join(self.path, "objects", sha[0:2], sha[2:4], sha)

    def open_object(self, sha):
        """Open an object by sha."""
        try:
            return open(self._sha_path(sha), "rb")
        except FileNotFoundError as exc:
            raise KeyError(sha) from exc

    def write_object(self, chunks):
        """Write an object.

        Returns: object SHA
        """
        sha = hashlib.sha256()
        tmpdir = os.path.join(self.path, "tmp")
        with tempfile.NamedTemporaryFile(dir=tmpdir, mode="wb", delete=False) as f:
            for chunk in chunks:
                sha.update(chunk)
                f.write(chunk)
            f.flush()
            tmppath = f.name
        path = self._sha_path(sha.hexdigest())
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        os.rename(tmppath, path)
        return sha.hexdigest()
