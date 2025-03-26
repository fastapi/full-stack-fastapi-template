from pathlib import Path

_PATH_TYPE_LABELS = {
    Path.is_dir: 'directory',
    Path.is_file: 'file',
    Path.is_mount: 'mount point',
    Path.is_symlink: 'symlink',
    Path.is_block_device: 'block device',
    Path.is_char_device: 'char device',
    Path.is_fifo: 'FIFO',
    Path.is_socket: 'socket',
}


def path_type_label(p: Path) -> str:
    """
    Find out what sort of thing a path is.
    """
    assert p.exists(), 'path does not exist'
    for method, name in _PATH_TYPE_LABELS.items():
        if method(p):
            return name

    return 'unknown'
