# object_store.py -- Object store for git objects
# Copyright (C) 2021 Jelmer Vernooij <jelmer@jelmer.uk>
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


"""Storage of repositories on GCS."""

import posixpath
import tempfile

from ..object_store import BucketBasedObjectStore
from ..pack import PACK_SPOOL_FILE_MAX_SIZE, Pack, PackData, load_pack_index_file

# TODO(jelmer): For performance, read ranges?


class GcsObjectStore(BucketBasedObjectStore):
    def __init__(self, bucket, subpath="") -> None:
        super().__init__()
        self.bucket = bucket
        self.subpath = subpath

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.bucket!r}, subpath={self.subpath!r})"

    def _remove_pack(self, name) -> None:
        self.bucket.delete_blobs(
            [posixpath.join(self.subpath, name) + "." + ext for ext in ["pack", "idx"]]
        )

    def _iter_pack_names(self):
        packs = {}
        for blob in self.bucket.list_blobs(prefix=self.subpath):
            name, ext = posixpath.splitext(posixpath.basename(blob.name))
            packs.setdefault(name, set()).add(ext)
        for name, exts in packs.items():
            if exts == {".pack", ".idx"}:
                yield name

    def _load_pack_data(self, name):
        b = self.bucket.blob(posixpath.join(self.subpath, name + ".pack"))
        f = tempfile.SpooledTemporaryFile(max_size=PACK_SPOOL_FILE_MAX_SIZE)
        b.download_to_file(f)
        f.seek(0)
        return PackData(name + ".pack", f)

    def _load_pack_index(self, name):
        b = self.bucket.blob(posixpath.join(self.subpath, name + ".idx"))
        f = tempfile.SpooledTemporaryFile(max_size=PACK_SPOOL_FILE_MAX_SIZE)
        b.download_to_file(f)
        f.seek(0)
        return load_pack_index_file(name + ".idx", f)

    def _get_pack(self, name):
        return Pack.from_lazy_objects(
            lambda: self._load_pack_data(name), lambda: self._load_pack_index(name)
        )

    def _upload_pack(self, basename, pack_file, index_file) -> None:
        idxblob = self.bucket.blob(posixpath.join(self.subpath, basename + ".idx"))
        datablob = self.bucket.blob(posixpath.join(self.subpath, basename + ".pack"))
        idxblob.upload_from_file(index_file)
        datablob.upload_from_file(pack_file)
