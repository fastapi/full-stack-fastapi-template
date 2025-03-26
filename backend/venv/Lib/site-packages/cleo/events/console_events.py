# The COMMAND event allows to attach listeners before any command
# is executed. It also allows the modification of the command and IO
# before it's handed to the command.
from __future__ import annotations


COMMAND = "console.command"

# The SIGNAL event allows some actions to be performed after
# the command execution is interrupted.
SIGNAL = "console.signal"

# The TERMINATE event allows listeners to be attached after the command
# is executed by the console.
TERMINATE = "console.terminate"

# The ERROR event occurs when an uncaught exception is raised.
#
# This event gives the ability to deal with the exception or to modify
# the raised exception.
ERROR = "console.error"
