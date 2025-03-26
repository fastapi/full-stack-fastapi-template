# sparse_patterns.py -- Sparse checkout pattern handling.
# Copyright (C) 2013 Jelmer Vernooij <jelmer@jelmer.uk>
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

"""Sparse checkout pattern handling."""

import os
from fnmatch import fnmatch

from .file import ensure_dir_exists


class SparseCheckoutConflictError(Exception):
    """Raised when local modifications would be overwritten by a sparse checkout operation."""


class BlobNotFoundError(Exception):
    """Raised when a requested blob is not found in the repository's object store."""


def determine_included_paths(repo, lines, cone):
    """Determine which paths in the index should be included based on either
    a full-pattern match or a cone-mode approach.

    Args:
      repo: A path to the repository or a Repo object.
      lines: A list of pattern lines (strings) from sparse-checkout config.
      cone: A bool indicating cone mode.

    Returns:
      A set of included path strings.
    """
    if cone:
        return compute_included_paths_cone(repo, lines)
    else:
        return compute_included_paths_full(repo, lines)


def compute_included_paths_full(repo, lines):
    """Use .gitignore-style parsing and matching to determine included paths.

    Each file path in the index is tested against the parsed sparse patterns.
    If it matches the final (most recently applied) positive pattern, it is included.

    Args:
      repo: A path to the repository or a Repo object.
      lines: A list of pattern lines (strings) from sparse-checkout config.

    Returns:
      A set of included path strings.
    """
    parsed = parse_sparse_patterns(lines)
    index = repo.open_index()
    included = set()
    for path_bytes, entry in index.items():
        path_str = path_bytes.decode("utf-8")
        # For .gitignore logic, match_gitignore_patterns returns True if 'included'
        if match_gitignore_patterns(path_str, parsed, path_is_dir=False):
            included.add(path_str)
    return included


def compute_included_paths_cone(repo, lines):
    """Implement a simplified 'cone' approach for sparse-checkout.

    By default, this can include top-level files, exclude all subdirectories,
    and re-include specified directories. The logic is less comprehensive than
    Git's built-in cone mode (recursive vs parent) and is essentially an implementation
    of the recursive cone mode.

    Args:
      repo: A path to the repository or a Repo object.
      lines: A list of pattern lines (strings), typically including entries like
        "/*", "!/*/", or "/mydir/".

    Returns:
      A set of included path strings.
    """
    include_top_level = False
    exclude_subdirs = False
    reinclude_dirs = set()

    for pat in lines:
        if pat == "/*":
            include_top_level = True
        elif pat == "!/*/":
            exclude_subdirs = True
        elif pat.startswith("/"):
            # strip leading '/' and trailing '/'
            d = pat.strip("/")
            if d:
                reinclude_dirs.add(d)

    index = repo.open_index()
    included = set()

    for path_bytes, entry in index.items():
        path_str = path_bytes.decode("utf-8")

        # Check if this is top-level (no slash) or which top_dir it belongs to
        if "/" not in path_str:
            # top-level file
            if include_top_level:
                included.add(path_str)
            continue

        top_dir = path_str.split("/", 1)[0]
        if exclude_subdirs:
            # subdirs are excluded unless they appear in reinclude_dirs
            if top_dir in reinclude_dirs:
                included.add(path_str)
        else:
            # if we never set exclude_subdirs, we might include everything by default
            # or handle partial subdir logic. For now, let's assume everything is included
            included.add(path_str)

    return included


def apply_included_paths(repo, included_paths, force=False):
    """Apply the sparse-checkout inclusion set to the index and working tree.

    This function updates skip-worktree bits in the index based on whether each
    path is included or not. It then adds or removes files in the working tree
    accordingly. If ``force=False``, files that have local modifications
    will cause an error instead of being removed.

    Args:
      repo: A path to the repository or a Repo object.
      included_paths: A set of paths (strings) that should remain included.
      force: Whether to forcibly remove locally modified files (default False).

    Returns:
      None
    """
    index = repo.open_index()
    normalizer = repo.get_blob_normalizer()

    def local_modifications_exist(full_path, index_entry):
        if not os.path.exists(full_path):
            return False
        try:
            with open(full_path, "rb") as f:
                disk_data = f.read()
        except OSError:
            return True
        try:
            blob = repo.object_store[index_entry.sha]
        except KeyError:
            return True
        norm_data = normalizer.checkin_normalize(disk_data, full_path)
        return norm_data != blob.data

    # 1) Update skip-worktree bits
    for path_bytes, entry in list(index.items()):
        path_str = path_bytes.decode("utf-8")
        if path_str in included_paths:
            entry.set_skip_worktree(False)
        else:
            entry.set_skip_worktree(True)
        index[path_bytes] = entry
    index.write()

    # 2) Reflect changes in the working tree
    for path_bytes, entry in list(index.items()):
        full_path = os.path.join(repo.path, path_bytes.decode("utf-8"))

        if entry.skip_worktree:
            # Excluded => remove if safe
            if os.path.exists(full_path):
                if not force and local_modifications_exist(full_path, entry):
                    raise SparseCheckoutConflictError(
                        f"Local modifications in {full_path} would be overwritten "
                        "by sparse checkout. Use force=True to override."
                    )
                try:
                    os.remove(full_path)
                except IsADirectoryError:
                    pass
                except FileNotFoundError:
                    pass
        else:
            # Included => materialize if missing
            if not os.path.exists(full_path):
                try:
                    blob = repo.object_store[entry.sha]
                except KeyError:
                    raise BlobNotFoundError(
                        f"Blob {entry.sha} not found for {path_bytes}."
                    )
                ensure_dir_exists(os.path.dirname(full_path))
                with open(full_path, "wb") as f:
                    f.write(blob.data)


def parse_sparse_patterns(lines):
    """Parse pattern lines from a sparse-checkout file (.git/info/sparse-checkout).

    This simplified parser:
      1. Strips comments (#...) and empty lines.
      2. Returns a list of (pattern, is_negation, is_dir_only, anchored) tuples.

    These lines are similar to .gitignore patterns but are used for sparse-checkout
    logic. This function strips comments and blank lines, identifies negation,
    anchoring, and directory-only markers, and returns data suitable for matching.

    Example:
      ``line = "/*.txt" -> ("/.txt", False, False, True)``
      ``line = "!/docs/" -> ("/docs/", True, True, True)``
      ``line = "mydir/" -> ("mydir/", False, True, False)`` not anchored, no leading "/"

    Args:
      lines: A list of raw lines (strings) from the sparse-checkout file.

    Returns:
      A list of tuples (pattern, negation, dir_only, anchored), representing
      the essential details needed to perform matching.
    """
    results = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue  # ignore comments and blank lines

        negation = line.startswith("!")
        if negation:
            line = line[1:]  # remove leading '!'

        anchored = line.startswith("/")
        if anchored:
            line = line[1:]  # remove leading '/'

        # If pattern ends with '/', we consider it directory-only
        # (like "docs/"). Real Git might treat it slightly differently,
        # but we'll simplify and mark it as "dir_only" if it ends in "/".
        dir_only = False
        if line.endswith("/"):
            dir_only = True
            line = line[:-1]

        results.append((line, negation, dir_only, anchored))
    return results


def match_gitignore_patterns(path_str, parsed_patterns, path_is_dir=False):
    """Check whether a path is included based on .gitignore-style patterns.

    This is a simplified approach that:
      1. Iterates over patterns in order.
      2. If a pattern matches, we set the "include" state depending on negation.
      3. Later matches override earlier ones.

    In a .gitignore sense, lines that do not start with '!' are "ignore" patterns,
    lines that start with '!' are "unignore" (re-include). But in sparse checkout,
    it's effectively reversed: a non-negation line is "include," negation is "exclude."
    However, many flows still rely on the same final logic: the last matching pattern
    decides "excluded" vs. "included."

    We'll interpret "include" as returning True, "exclude" as returning False.

    Each pattern can include negation (!), directory-only markers, or be anchored
    to the start of the path. The last matching pattern determines whether the
    path is ultimately included or excluded.

    Args:
      path_str: The path (string) to test.
      parsed_patterns: A list of (pattern, negation, dir_only, anchored) tuples
        as returned by parse_sparse_patterns.
      path_is_dir: Whether to treat the path as a directory (default False).

    Returns:
      True if the path is included by the last matching pattern, False otherwise.
    """
    # Start by assuming "excluded" (like a .gitignore starts by including everything
    # until matched, but for sparse-checkout we often treat unmatched as "excluded").
    # We will flip if we match an "include" pattern.
    is_included = False

    for pattern, negation, dir_only, anchored in parsed_patterns:
        forbidden_path = dir_only and not path_is_dir
        if path_str == pattern:
            if forbidden_path:
                continue
            else:
                matched = True
        else:
            matched = False
        # If dir_only is True and path_is_dir is False, we skip matching
        if dir_only and not matched:
            if path_str == pattern + "/":
                matched = not forbidden_path
            elif fnmatch(path_str, f"{pattern}/*"):
                matched = True  # root subpath (anchored or unanchored)
            elif not anchored:
                matched = fnmatch(path_str, f"*/{pattern}/*")  # unanchored subpath

        # If anchored is True, pattern should match from the start of path_str.
        # If not anchored, we can match anywhere.
        if anchored and not matched:
            # We match from the beginning. For example, pattern = "docs"
            # path_str = "docs/readme.md" -> start is "docs"
            # We'll just do a prefix check or prefix + slash check
            # Or you can do a partial fnmatch. We'll do a manual approach:
            if pattern == "":
                # Means it was just "/", which can happen if line was "/"
                # That might represent top-level only?
                # We'll skip for simplicity or treat it as a special case.
                continue
            elif path_str == pattern:
                matched = True
            elif path_str.startswith(pattern + "/"):
                matched = True
            else:
                matched = False
        elif not matched:
            # Not anchored: we can do a simple wildcard match or a substring match.
            # For simplicity, let's use Python's fnmatch:
            matched = fnmatch(path_str, pattern) or fnmatch(path_str, f"*/{pattern}")

        if matched:
            # If negation is True, that means 'exclude'. If negation is False, 'include'.
            is_included = not negation
            # The last matching pattern overrides, so we continue checking until the end.

    return is_included
