"""
Command name -> Command object dictionary able to choose most appropriate
command by partial name.
"""


from powercmd.command import Command
from powercmd.exceptions import InvalidInput
from powercmd.match_string import match_string


class CommandsDict(dict):
    """
    A container for Command objects that allows accessing them by name.

    Functionally, Mapping[str, Command].
    """
    def choose(self,
               short_cmd: str,
               verbose: bool = False) -> Command:
        """Returns a command handler that matches SHORT_CMD."""
        matches = match_string(short_cmd, self, verbose=verbose)

        if not matches:
            raise InvalidInput('no such command: %s' % (short_cmd,))
        if len(matches) > 1:
            raise InvalidInput('ambigious command: %s (possible: %s)'
                               % (short_cmd, ' '.join(matches)))
        return self[matches[0]]
