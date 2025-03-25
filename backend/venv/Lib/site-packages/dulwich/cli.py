#
# dulwich - Simple command-line interface to Dulwich
# Copyright (C) 2008-2011 Jelmer Vernooij <jelmer@jelmer.uk>
# vim: expandtab
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

"""Simple command-line interface to Dulwich>.

This is a very simple command-line wrapper for Dulwich. It is by
no means intended to be a full-blown Git command-line interface but just
a way to test Dulwich.
"""

import argparse
import optparse
import os
import signal
import sys
from getopt import getopt
from typing import TYPE_CHECKING, ClassVar, Optional

from dulwich import porcelain

from .client import GitProtocolError, get_transport_and_path
from .errors import ApplyDeltaError
from .index import Index
from .objectspec import parse_commit
from .pack import Pack, sha_to_hex
from .repo import Repo

if TYPE_CHECKING:
    from .objects import ObjectID
    from .refs import Ref


def signal_int(signal, frame) -> None:
    sys.exit(1)


def signal_quit(signal, frame) -> None:
    import pdb

    pdb.set_trace()


class Command:
    """A Dulwich subcommand."""

    def run(self, args) -> Optional[int]:
        """Run the command."""
        raise NotImplementedError(self.run)


class cmd_archive(Command):
    def run(self, args) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--remote",
            type=str,
            help="Retrieve archive from specified remote repo",
        )
        parser.add_argument("committish", type=str, nargs="?")
        args = parser.parse_args(args)
        if args.remote:
            client, path = get_transport_and_path(args.remote)
            client.archive(
                path,
                args.committish,
                sys.stdout.write,
                write_error=sys.stderr.write,
            )
        else:
            porcelain.archive(
                ".", args.committish, outstream=sys.stdout.buffer, errstream=sys.stderr
            )


class cmd_add(Command):
    def run(self, argv) -> None:
        parser = argparse.ArgumentParser()
        args = parser.parse_args(argv)

        porcelain.add(".", paths=args)


class cmd_rm(Command):
    def run(self, argv) -> None:
        parser = argparse.ArgumentParser()
        args = parser.parse_args(argv)

        porcelain.rm(".", paths=args)


class cmd_fetch_pack(Command):
    def run(self, argv) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--all", action="store_true")
        parser.add_argument("location", nargs="?", type=str)
        parser.add_argument("refs", nargs="*", type=str)
        args = parser.parse_args(argv)
        client, path = get_transport_and_path(args.location)
        r = Repo(".")
        if args.all:
            determine_wants = r.object_store.determine_wants_all
        else:

            def determine_wants(
                refs: dict[Ref, ObjectID], depth: Optional[int] = None
            ) -> list[ObjectID]:
                return [y.encode("utf-8") for y in args.refs if y not in r.object_store]

        client.fetch(path, r, determine_wants)


class cmd_fetch(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", [])
        dict(opts)
        client, path = get_transport_and_path(args.pop(0))
        r = Repo(".")

        def progress(msg: bytes) -> None:
            sys.stdout.buffer.write(msg)

        refs = client.fetch(path, r, progress=progress)
        print("Remote refs:")
        for item in refs.items():
            print("{} -> {}".format(*item))


class cmd_for_each_ref(Command):
    def run(self, args) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("pattern", type=str, nargs="?")
        args = parser.parse_args(args)
        for sha, object_type, ref in porcelain.for_each_ref(".", args.pattern):
            print(f"{sha.decode()} {object_type.decode()}\t{ref.decode()}")


class cmd_fsck(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", [])
        dict(opts)
        for obj, msg in porcelain.fsck("."):
            print(f"{obj}: {msg}")


class cmd_log(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        parser.add_option(
            "--reverse",
            dest="reverse",
            action="store_true",
            help="Reverse order in which entries are printed",
        )
        parser.add_option(
            "--name-status",
            dest="name_status",
            action="store_true",
            help="Print name/status for each changed file",
        )
        options, args = parser.parse_args(args)

        porcelain.log(
            ".",
            paths=args,
            reverse=options.reverse,
            name_status=options.name_status,
            outstream=sys.stdout,
        )


class cmd_diff(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", [])

        r = Repo(".")
        if args == []:
            commit_id = b"HEAD"
        else:
            commit_id = args[0]
        commit = parse_commit(r, commit_id)
        parent_commit = r[commit.parents[0]]
        porcelain.diff_tree(
            r, parent_commit.tree, commit.tree, outstream=sys.stdout.buffer
        )


class cmd_dump_pack(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", [])

        if args == []:
            print("Usage: dulwich dump-pack FILENAME")
            sys.exit(1)

        basename, _ = os.path.splitext(args[0])
        x = Pack(basename)
        print(f"Object names checksum: {x.name()}")
        print(f"Checksum: {sha_to_hex(x.get_stored_checksum())}")
        x.check()
        print(f"Length: {len(x)}")
        for name in x:
            try:
                print(f"\t{x[name]}")
            except KeyError as k:
                print(f"\t{name}: Unable to resolve base {k}")
            except ApplyDeltaError as e:
                print(f"\t{name}: Unable to apply delta: {e!r}")


class cmd_dump_index(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", [])

        if args == []:
            print("Usage: dulwich dump-index FILENAME")
            sys.exit(1)

        filename = args[0]
        idx = Index(filename)

        for o in idx:
            print(o, idx[o])


class cmd_init(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", ["bare"])
        kwopts = dict(opts)

        if args == []:
            path = os.getcwd()
        else:
            path = args[0]

        porcelain.init(path, bare=("--bare" in kwopts))


class cmd_clone(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        parser.add_option(
            "--bare",
            dest="bare",
            help="Whether to create a bare repository.",
            action="store_true",
        )
        parser.add_option(
            "--depth", dest="depth", type=int, help="Depth at which to fetch"
        )
        parser.add_option(
            "-b",
            "--branch",
            dest="branch",
            type=str,
            help=("Check out branch instead of branch pointed to by remote HEAD"),
        )
        parser.add_option(
            "--refspec",
            dest="refspec",
            type=str,
            help="References to fetch",
            action="append",
        )
        parser.add_option(
            "--filter",
            dest="filter_spec",
            type=str,
            help="git-rev-list-style object filter",
        )
        parser.add_option(
            "--protocol", dest="protocol", type=int, help="Git protocol version to use"
        )
        options, args = parser.parse_args(args)

        if args == []:
            print("usage: dulwich clone host:path [PATH]")
            sys.exit(1)

        source = args.pop(0)
        if len(args) > 0:
            target = args.pop(0)
        else:
            target = None

        try:
            porcelain.clone(
                source,
                target,
                bare=options.bare,
                depth=options.depth,
                branch=options.branch,
                refspec=options.refspec,
                filter_spec=options.filter_spec,
                protocol_version=options.protocol,
            )
        except GitProtocolError as e:
            print(f"{e}")


class cmd_commit(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", ["message"])
        kwopts = dict(opts)
        porcelain.commit(".", message=kwopts["--message"])


class cmd_commit_tree(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", ["message"])
        if args == []:
            print("usage: dulwich commit-tree tree")
            sys.exit(1)
        kwopts = dict(opts)
        porcelain.commit_tree(".", tree=args[0], message=kwopts["--message"])


class cmd_update_server_info(Command):
    def run(self, args) -> None:
        porcelain.update_server_info(".")


class cmd_symbolic_ref(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", ["ref-name", "force"])
        if not args:
            print("Usage: dulwich symbolic-ref REF_NAME [--force]")
            sys.exit(1)

        ref_name = args.pop(0)
        porcelain.symbolic_ref(".", ref_name=ref_name, force="--force" in args)


class cmd_pack_refs(Command):
    def run(self, argv) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--all", action="store_true")
        # ignored, we never prune
        parser.add_argument("--no-prune", action="store_true")

        args = parser.parse_args(argv)

        porcelain.pack_refs(".", all=args.all)


class cmd_show(Command):
    def run(self, argv) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("objectish", type=str, nargs="*")
        args = parser.parse_args(argv)
        porcelain.show(".", args.objectish or None)


class cmd_diff_tree(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", [])
        if len(args) < 2:
            print("Usage: dulwich diff-tree OLD-TREE NEW-TREE")
            sys.exit(1)
        porcelain.diff_tree(".", args[0], args[1])


class cmd_rev_list(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", [])
        if len(args) < 1:
            print("Usage: dulwich rev-list COMMITID...")
            sys.exit(1)
        porcelain.rev_list(".", args)


class cmd_tag(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        parser.add_option(
            "-a",
            "--annotated",
            help="Create an annotated tag.",
            action="store_true",
        )
        parser.add_option(
            "-s", "--sign", help="Sign the annotated tag.", action="store_true"
        )
        options, args = parser.parse_args(args)
        porcelain.tag_create(
            ".", args[0], annotated=options.annotated, sign=options.sign
        )


class cmd_repack(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", [])
        dict(opts)
        porcelain.repack(".")


class cmd_reset(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", ["hard", "soft", "mixed"])
        kwopts = dict(opts)
        mode = ""
        if "--hard" in kwopts:
            mode = "hard"
        elif "--soft" in kwopts:
            mode = "soft"
        elif "--mixed" in kwopts:
            mode = "mixed"
        porcelain.reset(".", mode=mode)


class cmd_daemon(Command):
    def run(self, args) -> None:
        from dulwich import log_utils

        from .protocol import TCP_GIT_PORT

        parser = optparse.OptionParser()
        parser.add_option(
            "-l",
            "--listen_address",
            dest="listen_address",
            default="localhost",
            help="Binding IP address.",
        )
        parser.add_option(
            "-p",
            "--port",
            dest="port",
            type=int,
            default=TCP_GIT_PORT,
            help="Binding TCP port.",
        )
        options, args = parser.parse_args(args)

        log_utils.default_logging_config()
        if len(args) >= 1:
            gitdir = args[0]
        else:
            gitdir = "."

        porcelain.daemon(gitdir, address=options.listen_address, port=options.port)


class cmd_web_daemon(Command):
    def run(self, args) -> None:
        from dulwich import log_utils

        parser = optparse.OptionParser()
        parser.add_option(
            "-l",
            "--listen_address",
            dest="listen_address",
            default="",
            help="Binding IP address.",
        )
        parser.add_option(
            "-p",
            "--port",
            dest="port",
            type=int,
            default=8000,
            help="Binding TCP port.",
        )
        options, args = parser.parse_args(args)

        log_utils.default_logging_config()
        if len(args) >= 1:
            gitdir = args[0]
        else:
            gitdir = "."

        porcelain.web_daemon(gitdir, address=options.listen_address, port=options.port)


class cmd_write_tree(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        sys.stdout.write("{}\n".format(porcelain.write_tree(".")))


class cmd_receive_pack(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        if len(args) >= 1:
            gitdir = args[0]
        else:
            gitdir = "."
        porcelain.receive_pack(gitdir)


class cmd_upload_pack(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        if len(args) >= 1:
            gitdir = args[0]
        else:
            gitdir = "."
        porcelain.upload_pack(gitdir)


class cmd_status(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        if len(args) >= 1:
            gitdir = args[0]
        else:
            gitdir = "."
        status = porcelain.status(gitdir)
        if any(names for (kind, names) in status.staged.items()):
            sys.stdout.write("Changes to be committed:\n\n")
            for kind, names in status.staged.items():
                for name in names:
                    sys.stdout.write(
                        f"\t{kind}: {name.decode(sys.getfilesystemencoding())}\n"
                    )
            sys.stdout.write("\n")
        if status.unstaged:
            sys.stdout.write("Changes not staged for commit:\n\n")
            for name in status.unstaged:
                sys.stdout.write(f"\t{name.decode(sys.getfilesystemencoding())}\n")
            sys.stdout.write("\n")
        if status.untracked:
            sys.stdout.write("Untracked files:\n\n")
            for name in status.untracked:
                sys.stdout.write(f"\t{name}\n")
            sys.stdout.write("\n")


class cmd_ls_remote(Command):
    def run(self, args) -> None:
        opts, args = getopt(args, "", [])
        if len(args) < 1:
            print("Usage: dulwich ls-remote URL")
            sys.exit(1)
        refs = porcelain.ls_remote(args[0])
        for ref in sorted(refs):
            sys.stdout.write(f"{ref}\t{refs[ref]}\n")


class cmd_ls_tree(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        parser.add_option(
            "-r",
            "--recursive",
            action="store_true",
            help="Recursively list tree contents.",
        )
        parser.add_option("--name-only", action="store_true", help="Only display name.")
        options, args = parser.parse_args(args)
        try:
            treeish = args.pop(0)
        except IndexError:
            treeish = None
        porcelain.ls_tree(
            ".",
            treeish,
            outstream=sys.stdout,
            recursive=options.recursive,
            name_only=options.name_only,
        )


class cmd_pack_objects(Command):
    def run(self, args) -> None:
        deltify = False
        reuse_deltas = True
        opts, args = getopt(args, "", ["stdout", "deltify", "no-reuse-deltas"])
        kwopts = dict(opts)
        if len(args) < 1 and "--stdout" not in kwopts.keys():
            print("Usage: dulwich pack-objects basename")
            sys.exit(1)
        object_ids = [line.strip() for line in sys.stdin.readlines()]
        if "--deltify" in kwopts.keys():
            deltify = True
        if "--no-reuse-deltas" in kwopts.keys():
            reuse_deltas = False
        if "--stdout" in kwopts.keys():
            packf = getattr(sys.stdout, "buffer", sys.stdout)
            idxf = None
            close = []
        else:
            basename = args[0]
            packf = open(basename + ".pack", "wb")
            idxf = open(basename + ".idx", "wb")
            close = [packf, idxf]
        porcelain.pack_objects(
            ".", object_ids, packf, idxf, deltify=deltify, reuse_deltas=reuse_deltas
        )
        for f in close:
            f.close()


class cmd_pull(Command):
    def run(self, args) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("from_location", type=str)
        parser.add_argument("refspec", type=str, nargs="*")
        parser.add_argument("--filter", type=str, nargs=1)
        parser.add_argument("--protocol", type=int, nargs=1)
        args = parser.parse_args(args)
        porcelain.pull(
            ".",
            args.from_location or None,
            args.refspec or None,
            filter_spec=args.filter,
            protocol_version=args.protocol_version or None,
        )


class cmd_push(Command):
    def run(self, argv) -> Optional[int]:
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--force", action="store_true", help="Force")
        parser.add_argument("to_location", type=str)
        parser.add_argument("refspec", type=str, nargs="*")
        args = parser.parse_args(argv)
        try:
            porcelain.push(
                ".", args.to_location, args.refspec or None, force=args.force
            )
        except porcelain.DivergedBranches:
            sys.stderr.write("Diverged branches; specify --force to override")
            return 1

        return None


class cmd_remote_add(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        porcelain.remote_add(".", args[0], args[1])


class SuperCommand(Command):
    subcommands: ClassVar[dict[str, type[Command]]] = {}
    default_command: ClassVar[Optional[type[Command]]] = None

    def run(self, args):
        if not args and not self.default_command:
            print(
                "Supported subcommands: {}".format(", ".join(self.subcommands.keys()))
            )
            return False
        cmd = args[0]
        try:
            cmd_kls = self.subcommands[cmd]
        except KeyError:
            print(f"No such subcommand: {args[0]}")
            return False
        return cmd_kls().run(args[1:])


class cmd_remote(SuperCommand):
    subcommands: ClassVar[dict[str, type[Command]]] = {
        "add": cmd_remote_add,
    }


class cmd_submodule_list(Command):
    def run(self, argv) -> None:
        parser = argparse.ArgumentParser()
        parser.parse_args(argv)
        for path, sha in porcelain.submodule_list("."):
            sys.stdout.write(f" {sha} {path}\n")


class cmd_submodule_init(Command):
    def run(self, argv) -> None:
        parser = argparse.ArgumentParser()
        parser.parse_args(argv)
        porcelain.submodule_init(".")


class cmd_submodule(SuperCommand):
    subcommands: ClassVar[dict[str, type[Command]]] = {
        "init": cmd_submodule_init,
    }

    default_command = cmd_submodule_init


class cmd_check_ignore(Command):
    def run(self, args):
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        ret = 1
        for path in porcelain.check_ignore(".", args):
            print(path)
            ret = 0
        return ret


class cmd_check_mailmap(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        for arg in args:
            canonical_identity = porcelain.check_mailmap(".", arg)
            print(canonical_identity)


class cmd_stash_list(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        for i, entry in porcelain.stash_list("."):
            print("stash@{{{}}}: {}".format(i, entry.message.rstrip("\n")))


class cmd_stash_push(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        porcelain.stash_push(".")
        print("Saved working directory and index state")


class cmd_stash_pop(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        porcelain.stash_pop(".")
        print("Restored working directory and index state")


class cmd_stash(SuperCommand):
    subcommands: ClassVar[dict[str, type[Command]]] = {
        "list": cmd_stash_list,
        "pop": cmd_stash_pop,
        "push": cmd_stash_push,
    }


class cmd_ls_files(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        for name in porcelain.ls_files("."):
            print(name)


class cmd_describe(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        options, args = parser.parse_args(args)
        print(porcelain.describe("."))


class cmd_help(Command):
    def run(self, args) -> None:
        parser = optparse.OptionParser()
        parser.add_option(
            "-a",
            "--all",
            dest="all",
            action="store_true",
            help="List all commands.",
        )
        options, args = parser.parse_args(args)

        if options.all:
            print("Available commands:")
            for cmd in sorted(commands):
                print(f"  {cmd}")
        else:
            print(
                """\
The dulwich command line tool is currently a very basic frontend for the
Dulwich python module. For full functionality, please see the API reference.

For a list of supported commands, see 'dulwich help -a'.
"""
            )


commands = {
    "add": cmd_add,
    "archive": cmd_archive,
    "check-ignore": cmd_check_ignore,
    "check-mailmap": cmd_check_mailmap,
    "clone": cmd_clone,
    "commit": cmd_commit,
    "commit-tree": cmd_commit_tree,
    "describe": cmd_describe,
    "daemon": cmd_daemon,
    "diff": cmd_diff,
    "diff-tree": cmd_diff_tree,
    "dump-pack": cmd_dump_pack,
    "dump-index": cmd_dump_index,
    "fetch-pack": cmd_fetch_pack,
    "fetch": cmd_fetch,
    "for-each-ref": cmd_for_each_ref,
    "fsck": cmd_fsck,
    "help": cmd_help,
    "init": cmd_init,
    "log": cmd_log,
    "ls-files": cmd_ls_files,
    "ls-remote": cmd_ls_remote,
    "ls-tree": cmd_ls_tree,
    "pack-objects": cmd_pack_objects,
    "pack-refs": cmd_pack_refs,
    "pull": cmd_pull,
    "push": cmd_push,
    "receive-pack": cmd_receive_pack,
    "remote": cmd_remote,
    "repack": cmd_repack,
    "reset": cmd_reset,
    "rev-list": cmd_rev_list,
    "rm": cmd_rm,
    "show": cmd_show,
    "stash": cmd_stash,
    "status": cmd_status,
    "symbolic-ref": cmd_symbolic_ref,
    "submodule": cmd_submodule,
    "tag": cmd_tag,
    "update-server-info": cmd_update_server_info,
    "upload-pack": cmd_upload_pack,
    "web-daemon": cmd_web_daemon,
    "write-tree": cmd_write_tree,
}


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) < 1:
        print("Usage: dulwich <{}> [OPTIONS...]".format("|".join(commands.keys())))
        return 1

    cmd = argv[0]
    try:
        cmd_kls = commands[cmd]
    except KeyError:
        print(f"No such subcommand: {cmd}")
        return 1
    # TODO(jelmer): Return non-0 on errors
    return cmd_kls().run(argv[1:])


def _main() -> None:
    if "DULWICH_PDB" in os.environ and getattr(signal, "SIGQUIT", None):
        signal.signal(signal.SIGQUIT, signal_quit)  # type: ignore
    signal.signal(signal.SIGINT, signal_int)

    sys.exit(main())


if __name__ == "__main__":
    _main()
