# log_utils.py -- Logging utilities for Dulwich
# Copyright (C) 2010 Google, Inc.
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

"""Logging utilities for Dulwich.

Any module that uses logging needs to do compile-time initialization to set up
the logging environment. Since Dulwich is also used as a library, clients may
not want to see any logging output. In that case, we need to use a special
handler to suppress spurious warnings like "No handlers could be found for
logger dulwich.foo".

For details on the _NullHandler approach, see:
http://docs.python.org/library/logging.html#configuring-logging-for-a-library

For many modules, the only function from the logging module they need is
getLogger; this module exports that function for convenience. If a calling
module needs something else, it can import the standard logging module
directly.
"""

import logging
import sys

getLogger = logging.getLogger


class _NullHandler(logging.Handler):
    """No-op logging handler to avoid unexpected logging warnings."""

    def emit(self, record) -> None:
        pass


_NULL_HANDLER = _NullHandler()
_DULWICH_LOGGER = getLogger("dulwich")
_DULWICH_LOGGER.addHandler(_NULL_HANDLER)


def default_logging_config() -> None:
    """Set up the default Dulwich loggers."""
    remove_null_handler()
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s: %(message)s",
    )


def remove_null_handler() -> None:
    """Remove the null handler from the Dulwich loggers.

    If a caller wants to set up logging using something other than
    default_logging_config, calling this function first is a minor optimization
    to avoid the overhead of using the _NullHandler.
    """
    _DULWICH_LOGGER.removeHandler(_NULL_HANDLER)
