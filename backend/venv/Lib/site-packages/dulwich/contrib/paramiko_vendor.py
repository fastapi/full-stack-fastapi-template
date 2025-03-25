# paramiko_vendor.py -- paramiko implementation of the SSHVendor interface
# Copyright (C) 2013 Aaron O'Mullan <aaron.omullan@friendco.de>
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

"""Paramiko SSH support for Dulwich.

To use this implementation as the SSH implementation in Dulwich, override
the dulwich.client.get_ssh_vendor attribute:

  >>> from dulwich import client as _mod_client
  >>> from dulwich.contrib.paramiko_vendor import ParamikoSSHVendor
  >>> _mod_client.get_ssh_vendor = ParamikoSSHVendor

This implementation is experimental and does not have any tests.
"""

import paramiko
import paramiko.client


class _ParamikoWrapper:
    def __init__(self, client, channel) -> None:
        self.client = client
        self.channel = channel

        # Channel must block
        self.channel.setblocking(True)

    @property
    def stderr(self):
        return self.channel.makefile_stderr("rb")

    def can_read(self):
        return self.channel.recv_ready()

    def write(self, data):
        return self.channel.sendall(data)

    def read(self, n=None):
        data = self.channel.recv(n)
        data_len = len(data)

        # Closed socket
        if not data:
            return b""

        # Read more if needed
        if n and data_len < n:
            diff_len = n - data_len
            return data + self.read(diff_len)
        return data

    def close(self) -> None:
        self.channel.close()


class ParamikoSSHVendor:
    # http://docs.paramiko.org/en/2.4/api/client.html

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    def run_command(
        self,
        host,
        command,
        username=None,
        port=None,
        password=None,
        pkey=None,
        key_filename=None,
        protocol_version=None,
        **kwargs,
    ):
        client = paramiko.SSHClient()

        connection_kwargs = {"hostname": host}
        connection_kwargs.update(self.kwargs)
        if username:
            connection_kwargs["username"] = username
        if port:
            connection_kwargs["port"] = port
        if password:
            connection_kwargs["password"] = password
        if pkey:
            connection_kwargs["pkey"] = pkey
        if key_filename:
            connection_kwargs["key_filename"] = key_filename
        connection_kwargs.update(kwargs)

        policy = paramiko.client.MissingHostKeyPolicy()
        client.set_missing_host_key_policy(policy)
        client.connect(**connection_kwargs)

        # Open SSH session
        channel = client.get_transport().open_session()

        if protocol_version is None or protocol_version == 2:
            channel.set_environment_variable(name="GIT_PROTOCOL", value="version=2")

        # Run commands
        channel.exec_command(command)

        return _ParamikoWrapper(client, channel)
