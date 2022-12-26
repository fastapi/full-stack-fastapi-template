from enum import Enum


class BaseEnum(str, Enum):
    # noinspection PyMethodParameters
    # cf https://gitter.im/tiangolo/fastapi?at=5d775f4050508949d30b6eec
    def _generate_next_value_(name, start, count, last_values) -> str:  # type: ignore
        """
        Uses the name as the automatic value, rather than an integer

        See https://docs.python.org/3/library/enum.html#using-automatic-values for reference
        """
        return name

    @classmethod
    def as_dict(cls):
        member_dict = {role: member.value for role, member in cls.__members__.items()}
        return member_dict

    @classmethod
    def _missing_(cls, value):
        # https://stackoverflow.com/a/68311691/295606
        for member in cls:
            if member.value.upper() == value.upper():
                return member
