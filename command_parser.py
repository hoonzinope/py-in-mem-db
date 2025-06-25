from command.registry import parse_command

class Parser:
    @staticmethod
    def parse(cmd):
        """
        Parses a command string and returns the corresponding command object.

        :param cmd: The command string to parse.
        :return: An instance of the command class or None if the command is invalid.
        """
        return parse_command(cmd)