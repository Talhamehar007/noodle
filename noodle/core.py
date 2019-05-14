from ._formatter import get_command_help, get_master_help
from ._messages import CliMsg, DescriptionMsg, ErrorMsg
from ._parser import Parser
from .io import output

# import pysnooper


_GLOBAL_OPTIONS = {
    "version": "Display this application version",
    "help": "Display this help message",
}

parse = Parser()


class Base:
    """Base class for both, Master and Command"""

    def _get_doc(cls):
        if cls.__doc__:
            return cls.__doc__.strip()


class Master(Base):
    """Global CLI configuration."""

    cover = None  # TODO: print something nice

    app_name = None
    version = "0.1.0"
    options = None  # custom user options

    def __init__(self):
        self.app_name = self._app_name
        self._command = parse.get_command
        self._commands = {}
        self.flags = parse.get_flags
        self.default_options = parse.parse_options(_GLOBAL_OPTIONS)
        self.options = self._user_options

    @property
    def _app_name(self):
        if not self.app_name:
            return parse.get_app_name

        return self.app_name

    @property
    def _user_options(self):
        if self.options:
            return parse.parse_options(self.options)

    def _main_help(self):
        """Generate the Info message for the CLI app."""
        description = self._get_doc()
        if description is None:
            description = DescriptionMsg.no_description()

        return get_master_help(
            description, self._commands, self.default_options, self.options
        )

    def _execute_command(self):
        """Execute a registered Command."""
        if self._command in self._commands.keys():
            return self._commands[self._command]()

        output(ErrorMsg.wrong_command(self._command))

    def _execute_flag(self):
        """Execute a Flag (default or user defined)"""
        # TODO fix: undefined flag after a command prints help
        # HINT: this is because before the check for the flag the command is
        # executed (`_execute_command`). To output the expected
        # error message, create a check for flags inside the Command class.

        if "-h" in self.flags or "--help" in self.flags:
            output(self._main_help())

        elif "-v" in self.flags or "--version" in self.flags:
            output(CliMsg.version(self.app_name, self.version))

        else:
            # TODO: this shit is hardcoded and will bring doom if I don't fix it.
            output(ErrorMsg.wrong_command(self.flags[0]))

    def register(self, *args):
        """Register all the commands."""
        [self._commands.setdefault(command.command_name, command) for command in args]

    def run(self):
        """Execute the Command Line Interface."""
        if self._command:
            return self._execute_command()

        # provided_flags = parse.get_flags:
        elif self.flags:
            return self._execute_flag()

        output(self._main_help())


class Command(Base):
    """Base class for implementing Commands."""

    command_name = None  # str: caller of the command
    argument = None  # dict: {name: help} provided by the user
    options = None  # dict: {name: help} provided by the user

    def __init__(self):
        self.argv_argument = parse.get_argument  # Terminal argvs
        self.flags = parse.get_flags
        self.options = self._command_options
        self._run()

    @property
    def _command_options(self):
        if self.options:
            return parse.parse_options(self.options)

    def _command_help(self):
        """Generate the help message."""
        description = self._get_doc()
        if description is None:
            description = DescriptionMsg.no_description(self.command_name)

        help_msg = get_command_help(
            description, self.argument, self.command_name, self.options
        )
        output(help_msg)

    def handler(self):
        """The handler of the command."""
        raise NotImplementedError()

    def _run(self):
        """
        If an argument is provided, the dict in `self.argument` (defined
        by the user) is override with the argument (sys.argv) to be used on
        the `handler()` method. Else, generate and print the help.
        """
        # print(self.argv_argument)
        # TODO use len to turn self.argument to None if self.argv_argument is
        # an empty list. May be usefull letter on.
        if self.argv_argument:
            # `self.argv_argument` return a list of arguments. For now, to
            # retrieve the argument, is hardcoded to the first element of
            # the list. This wont work if the user need a a list of arguments.
            # Maybe a method on parse.get_argument (_parser.py).
            self.argument = self.argv_argument[0]
            # print(self.argument)
            return self.handler()

        return self._command_help()
