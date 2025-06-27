from command.command import Command
from command.registry import register_command
from logger import logger

@register_command("show-alias")
class ShowAlias(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = logger(self.__class__.__name__)

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if not self.original_command:
            self.logger.log("No command provided for showing aliases.")
            return "No command provided for showing aliases."

        return self._show_alias()

    def _show_alias(self):
        alias_command = self.memdb.alias_command
        if not alias_command:
            self.logger.log("No aliases set.")
            return "No aliases set."

        alias_list = [f"{alias}: {command}" for alias, command in alias_command.items()]
        return "\n".join(alias_list)