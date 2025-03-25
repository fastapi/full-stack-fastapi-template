from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import List


if TYPE_CHECKING:
    from crashtest.frame import Frame


class FrameCollection(List[Any]):
    def __init__(self, frames: list[Frame] | None = None, count: int = 0) -> None:
        if frames is None:
            frames = []

        super().__init__(frames)

        self._count = count

    @property
    def repetitions(self) -> int:
        return self._count - 1

    def is_repeated(self) -> bool:
        return self._count > 1

    def increment_count(self, increment: int = 1) -> FrameCollection:
        self._count += increment

        return self

    def compact(self) -> list[FrameCollection]:
        """
        Compacts the frames to deduplicate recursive calls.
        """
        collections = []
        current_collection = FrameCollection()

        i = 0
        while i < len(self) - 1:
            frame = self[i]
            if frame in self[i + 1 :]:
                duplicate_indices = []
                for sub_index, sub_frame in enumerate(self[i + 1 :]):
                    if frame == sub_frame:
                        duplicate_indices.append(sub_index + i + 1)

                found_duplicate = False
                for duplicate_index in duplicate_indices:
                    collection = FrameCollection(self[i:duplicate_index])
                    if collection == current_collection:
                        current_collection.increment_count()
                        i = duplicate_index
                        found_duplicate = True
                        break

                if found_duplicate:
                    continue

                collections.append(current_collection)
                current_collection = FrameCollection(self[i : duplicate_indices[0]])

                i = duplicate_indices[0]

                continue

            if current_collection.is_repeated():
                collections.append(current_collection)
                current_collection = FrameCollection()

            current_collection.append(frame)
            i += 1

        collections.append(current_collection)

        return collections
