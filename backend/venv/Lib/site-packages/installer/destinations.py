"""Handles all file writing and post-installation processing."""

import compileall
import io
import os
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    BinaryIO,
    Collection,
    Dict,
    Iterable,
    Optional,
    Tuple,
    Union,
)

from installer.records import Hash, RecordEntry
from installer.scripts import Script
from installer.utils import (
    Scheme,
    construct_record_file,
    copyfileobj_with_hashing,
    fix_shebang,
    make_file_executable,
)

if TYPE_CHECKING:
    from installer.scripts import LauncherKind, ScriptSection


class WheelDestination:
    """Handles writing the unpacked files, script generation and ``RECORD`` generation.

    Subclasses provide the concrete script generation logic, as well as the RECORD file
    (re)writing.
    """

    def write_script(
        self, name: str, module: str, attr: str, section: "ScriptSection"
    ) -> RecordEntry:
        """Write a script in the correct location to invoke given entry point.

        :param name: name of the script
        :param module: module path, to load the entry point from
        :param attr: final attribute access, for the entry point
        :param section: Denotes the "entry point section" where this was specified.
            Valid values are ``"gui"`` and ``"console"``.
        :type section: str

        Example usage/behaviour::

            >>> dest.write_script("pip", "pip._internal.cli", "main", "console")

        """
        raise NotImplementedError

    def write_file(
        self,
        scheme: Scheme,
        path: Union[str, "os.PathLike[str]"],
        stream: BinaryIO,
        is_executable: bool,
    ) -> RecordEntry:
        """Write a file to correct ``path`` within the ``scheme``.

        :param scheme: scheme to write the file in (like "purelib", "platlib" etc).
        :param path: path within that scheme
        :param stream: contents of the file
        :param is_executable: whether the file should be made executable

        The stream would be closed by the caller, after this call.

        Example usage/behaviour::

            >>> with open("__init__.py") as stream:
            ...     dest.write_file("purelib", "pkg/__init__.py", stream)

        """
        raise NotImplementedError

    def finalize_installation(
        self,
        scheme: Scheme,
        record_file_path: str,
        records: Iterable[Tuple[Scheme, RecordEntry]],
    ) -> None:
        """Finalize installation, after all the files are written.

        Handles (re)writing of the ``RECORD`` file.

        :param scheme: scheme to write the ``RECORD`` file in
        :param record_file_path: path of the ``RECORD`` file with that scheme
        :param records: entries to write to the ``RECORD`` file

        Example usage/behaviour::

            >>> dest.finalize_installation("purelib")

        """
        raise NotImplementedError


class SchemeDictionaryDestination(WheelDestination):
    """Destination, based on a mapping of {scheme: file-system-path}."""

    def __init__(
        self,
        scheme_dict: Dict[str, str],
        interpreter: str,
        script_kind: "LauncherKind",
        hash_algorithm: str = "sha256",
        bytecode_optimization_levels: Collection[int] = (),
        destdir: Optional[str] = None,
    ) -> None:
        """Construct a ``SchemeDictionaryDestination`` object.

        :param scheme_dict: a mapping of {scheme: file-system-path}
        :param interpreter: the interpreter to use for generating scripts
        :param script_kind: the "kind" of launcher script to use
        :param hash_algorithm: the hashing algorithm to use, which is a member
            of :any:`hashlib.algorithms_available` (ideally from
            :any:`hashlib.algorithms_guaranteed`).
        :param bytecode_optimization_levels: Compile cached bytecode for
            installed .py files with these optimization levels. The bytecode
            is specific to the minor version of Python (e.g. 3.10) used to
            generate it.
        :param destdir: A staging directory in which to write all files. This
            is expected to be the filesystem root at runtime, so embedded paths
            will be written as though this was the root.
        """
        self.scheme_dict = scheme_dict
        self.interpreter = interpreter
        self.script_kind = script_kind
        self.hash_algorithm = hash_algorithm
        self.bytecode_optimization_levels = bytecode_optimization_levels
        self.destdir = destdir

    def _path_with_destdir(self, scheme: Scheme, path: str) -> str:
        file = os.path.join(self.scheme_dict[scheme], path)
        if self.destdir is not None:
            file_path = Path(file)
            rel_path = file_path.relative_to(file_path.anchor)
            return os.path.join(self.destdir, rel_path)
        return file

    def write_to_fs(
        self,
        scheme: Scheme,
        path: str,
        stream: BinaryIO,
        is_executable: bool,
    ) -> RecordEntry:
        """Write contents of ``stream`` to the correct location on the filesystem.

        :param scheme: scheme to write the file in (like "purelib", "platlib" etc).
        :param path: path within that scheme
        :param stream: contents of the file
        :param is_executable: whether the file should be made executable

        - Ensures that an existing file is not being overwritten.
        - Hashes the written content, to determine the entry in the ``RECORD`` file.
        """
        target_path = self._path_with_destdir(scheme, path)
        if os.path.exists(target_path):
            message = f"File already exists: {target_path}"
            raise FileExistsError(message)

        parent_folder = os.path.dirname(target_path)
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)

        with open(target_path, "wb") as f:
            hash_, size = copyfileobj_with_hashing(stream, f, self.hash_algorithm)

        if is_executable:
            make_file_executable(target_path)

        return RecordEntry(path, Hash(self.hash_algorithm, hash_), size)

    def write_file(
        self,
        scheme: Scheme,
        path: Union[str, "os.PathLike[str]"],
        stream: BinaryIO,
        is_executable: bool,
    ) -> RecordEntry:
        """Write a file to correct ``path`` within the ``scheme``.

        :param scheme: scheme to write the file in (like "purelib", "platlib" etc).
        :param path: path within that scheme
        :param stream: contents of the file
        :param is_executable: whether the file should be made executable

        - Changes the shebang for files in the "scripts" scheme.
        - Uses :py:meth:`SchemeDictionaryDestination.write_to_fs` for the
          filesystem interaction.
        """
        path_ = os.fspath(path)

        if scheme == "scripts":
            with fix_shebang(stream, self.interpreter) as stream_with_different_shebang:
                return self.write_to_fs(
                    scheme, path_, stream_with_different_shebang, is_executable
                )

        return self.write_to_fs(scheme, path_, stream, is_executable)

    def write_script(
        self, name: str, module: str, attr: str, section: "ScriptSection"
    ) -> RecordEntry:
        """Write a script to invoke an entrypoint.

        :param name: name of the script
        :param module: module path, to load the entry point from
        :param attr: final attribute access, for the entry point
        :param section: Denotes the "entry point section" where this was specified.
            Valid values are ``"gui"`` and ``"console"``.
        :type section: str

        - Generates a launcher using :any:`Script.generate`.
        - Writes to the "scripts" scheme.
        - Uses :py:meth:`SchemeDictionaryDestination.write_to_fs` for the
          filesystem interaction.
        """
        script = Script(name, module, attr, section)
        script_name, data = script.generate(self.interpreter, self.script_kind)

        with io.BytesIO(data) as stream:
            entry = self.write_to_fs(
                Scheme("scripts"), script_name, stream, is_executable=True
            )

            path = self._path_with_destdir(Scheme("scripts"), script_name)
            mode = os.stat(path).st_mode
            mode |= (mode & 0o444) >> 2
            os.chmod(path, mode)

            return entry

    def _compile_bytecode(self, scheme: Scheme, record: RecordEntry) -> None:
        """Compile bytecode for a single .py file."""
        if scheme not in ("purelib", "platlib"):
            return

        target_path = self._path_with_destdir(scheme, record.path)
        dir_path_to_embed = os.path.dirname(  # Without destdir
            os.path.join(self.scheme_dict[scheme], record.path)
        )
        for level in self.bytecode_optimization_levels:
            compileall.compile_file(
                target_path, optimize=level, quiet=1, ddir=dir_path_to_embed
            )

    def finalize_installation(
        self,
        scheme: Scheme,
        record_file_path: str,
        records: Iterable[Tuple[Scheme, RecordEntry]],
    ) -> None:
        """Finalize installation, by writing the ``RECORD`` file & compiling bytecode.

        :param scheme: scheme to write the ``RECORD`` file in
        :param record_file_path: path of the ``RECORD`` file with that scheme
        :param records: entries to write to the ``RECORD`` file
        """

        def prefix_for_scheme(file_scheme: str) -> Optional[str]:
            if file_scheme == scheme:
                return None
            path = os.path.relpath(
                self.scheme_dict[file_scheme],
                start=self.scheme_dict[scheme],
            )
            return path + "/"

        record_list = list(records)
        with construct_record_file(record_list, prefix_for_scheme) as record_stream:
            self.write_to_fs(
                scheme, record_file_path, record_stream, is_executable=False
            )

        for scheme, record in record_list:
            self._compile_bytecode(scheme, record)
