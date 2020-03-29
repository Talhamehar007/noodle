import sys

from ._formatter import get_command_help, get_master_help
from ._messages import CliMsg, DescriptionMsg, ErrorMsg
from ._parser import Parser
from .io import output


_GLOBAL_OPTIONS = {
    "version": "Display this application version",
    "help": "Display this help message",
}

_COMMAND_OPTIONS = {"help": "Display this help message"}

parse = Parser()


class Base:
    """
    Base class for both, Master and Command
    """

    def __init__(self, options, user_passed_options):
        # user-defined options
        self.options = parse.parse_options(self.options)

        # options passed on the command line
        self.user_passed_options = parse.get_options

    def _get_doc(self):
        if self.__doc__:
            return self.__doc__.strip()


class Master(Base):
    """
    Global CLI configuration.
    """

    cover = None  # TODO: print a nice cover
    app_name = None
    options = None
    version = "0.1.0"

    def __init__(self, options=None, user_passed_options=None):
        # user-defined and passed options
        super().__init__(options, user_passed_options)
        self.passed_command = parse.get_command

        # all the registered commands (from self.register())
        self._commands = {}

        # common options like --help or --version
        self.default_options = parse.parse_options(_GLOBAL_OPTIONS)

        # if app_name is None, get the name of the script
        if not self.app_name:
            self.app_name = parse.get_app_name

    def _main_help(self):
        """
        Generate the Info message for the CLI app.
        """
        description = self._get_doc()
        if description is None:
            description = DescriptionMsg.no_description()

        return get_master_help(
            description, self._commands, self.default_options, self.options
        )

    def _execute_command(self):
        """
        Execute a registered Command.
        """
        if self.passed_command in self._commands.keys():
            return self._commands[self.passed_command]()

        output(ErrorMsg.wrong_command(self.passed_command))

    def _execute_flag(self):
        """
        Execute a Flag (default or user defined)
        """
        if "-h" in self.user_passed_options or "--help" in self.user_passed_options:
            output(self._main_help())

        elif "-v" in self.user_passed_options or "--version" in self.user_passed_options:
            output(CliMsg.version(self.app_name, self.version))

        else:
            # TODO: this shit is hardcoded and will bring doom if I don't fix it.
            output(ErrorMsg.wrong_option(self.user_passed_options[0]))

    def register(self, *args):
        """
        Register a group of commands.
        """
        [self._commands.setdefault(command.command_name, command) for command in args]

    def run(self):
        """
        Execute the Command Line Interface.
        """
        if self.passed_command:
            return self._execute_command()

        elif self.user_passed_options:
            return self._execute_flag()

        output(self._main_help())


class Command(Base):
    """
    Base class for implementing Commands.
    """

    command_name = None  # str: caller of the command
    argument = None  # dict: {name: help} user defined
    options = None  # dict: {name: help} user defined

    def __init__(self, options=None, user_passed_options=None):
        # user-defined and passed options
        super().__init__(options, user_passed_options)

        # arguments passed on the command line
        self.passed_arguments = parse.get_argument

        # options shared by all the commands
        self.default_options = parse.parse_options(_COMMAND_OPTIONS)

        self._run()

    def _command_help(self):
        """
        Generate the help message.
        """
        description = self._get_doc()
        if description is None:
            description = DescriptionMsg.no_description(self.command_name)

        help_msg = get_command_help(
            description,
            self.argument,
            self.command_name,
            self.default_options,
            self.options,
        )
        output(help_msg)
        sys.exit()

    def handler(self):
        """
        The handler of the command.
        """
        raise NotImplementedError()

    def option(self, option):
        """
        Return True/False if the option valid.
        """
        # user-defined options are in self.options and passed option in
        # self.user_passed_options. Option can be  short (self.options[0].short_flag)
        # or long (self.options[0].long_flag)
        for opt in self.options:
            if opt.name == option:
                if opt.short_flag in self.user_passed_options:
                    return True
                elif opt.long_flag in self.user_passed_options:
                    return True

        return False

    def check_options(self):
        # TODO hardcoded for now
        if "-h" in self.user_passed_options or "--help" in self.user_passed_options:
            self._command_help()

        # if the option is found in short or long flag, return to _run()
        if self.options:
            for opt in self.options:
                if opt.short_flag in self.user_passed_options:
                    return
                if opt.long_flag in self.user_passed_options:
                    return

        # else, output an OptionNotFound warning and exit the program
        output(ErrorMsg.wrong_option(self.user_passed_options[0]))
        sys.exit()

    def _run(self):
        """
        If an argument is provided, the dict in `self.argument` (defined
        by the user) is override with the argument (sys.argv) to be used on
        the `handler()` method. Else, generate and print the help.
        """
        # check for passed options, if invalid output an OptionNotFound warning
        if self.user_passed_options:
            self.check_options()

        # check if an argument is needed to execute a command, and
        # if not, and one is passed anyway, output an ArgumentNeeded warning
        if self.argument and not self.passed_arguments:
            argument_name = [k for k in self.argument.keys()]
            output(ErrorMsg.no_argument(argument_name[0]))
            return

        # if the command don't need arguments, but one is passed anyway
        # output a TooManyArguments warning
        if self.passed_arguments and not self.argument:
            output(ErrorMsg.too_many_arguments(self.command_name))
            return

        # if the command don't need arguments to execute
        if not self.argument:
            return self.handler()

        if self.passed_arguments:
            # `self.passed_arguments` return a list of arguments. For now, to
            # retrieve the argument, I hardcoded to the first element of
            # the list. This wont work if the user need a a list of arguments.
            # Maybe a method on parse.get_argument (_parser.py).
            self.argument = self.passed_arguments[0]
            return self.handler()

        return self._command_help()
