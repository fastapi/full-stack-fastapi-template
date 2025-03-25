# testing/warnings.py
# Copyright (C) 2005-2021 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import warnings

from sqlalchemy import exc as sa_exc


def setup_filters():
    """Set global warning behavior for the test suite."""

    warnings.resetwarnings()

    warnings.filterwarnings("error", category=sa_exc.SADeprecationWarning)
    warnings.filterwarnings("error", category=sa_exc.SAWarning)

    # some selected deprecations...
    warnings.filterwarnings("error", category=DeprecationWarning)
    try:
        import pytest
    except ImportError:
        pass
    else:
        warnings.filterwarnings(
            "once", category=pytest.PytestDeprecationWarning
        )
