from __future__ import annotations


class PythonVersionError(Exception):
    pass


class PythonVersionNotFoundError(PythonVersionError):
    def __init__(self, expected: str) -> None:
        super().__init__(f"Could not find the python executable {expected}")


class NoCompatiblePythonVersionFoundError(PythonVersionError):
    def __init__(self, expected: str, given: str | None = None) -> None:
        if given:
            message = (
                f"The specified Python version ({given}) "
                f"is not supported by the project ({expected}).\n"
                "Please choose a compatible version "
                "or loosen the python constraint specified "
                "in the pyproject.toml file."
            )
        else:
            message = (
                "Poetry was unable to find a compatible version. "
                "If you have one, you can explicitly use it "
                'via the "env use" command.'
            )

        super().__init__(message)


class InvalidCurrentPythonVersionError(PythonVersionError):
    def __init__(self, expected: str, given: str) -> None:
        message = (
            f"Current Python version ({given}) "
            f"is not allowed by the project ({expected}).\n"
            'Please change python executable via the "env use" command.'
        )

        super().__init__(message)
