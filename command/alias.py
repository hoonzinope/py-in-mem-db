from command.command import Command
from command.registry import register_command, COMMANDS

@register_command("alias")
class Alias(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.not_alias_command = ["alias", "load"]
        self.command_list = [c for c  in COMMANDS.keys() if c not in self.not_alias_command]
        self.alias_command = {}

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.alias_command = self.memdb.alias_command

        self.persistence_manager = persistence_manager
        if not self.original_command:
            return "No command provided for alias."

        result = self._set_alias(self.original_command)
        if self.persistence_manager:
            self.persistence_manager.save_alias(self.alias_command)
        return result

    def _set_alias(self, cmd):
        parts = cmd.split()
        if len(parts) != 3:
            return "Invalid alias command format. Use: alias <alias_name> <command>"

        alias_name = parts[1]
        command = parts[2]

        if alias_name in self.not_alias_command or command in self.not_alias_command:
            return "Cannot create alias for reserved commands. ({})".format(self.not_alias_command)

        if alias_name in self.alias_command:
            return f"Alias '{alias_name}' already exists."

        if command not in self.command_list:
            return f"Command '{command}' is not a valid command."

        self.alias_command[alias_name] = command
        return f"Alias '{alias_name}' set for command '{command}'."