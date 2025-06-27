from command.command import Command
from command.registry import register_command
from logger import Logger

@register_command("show-alias")
class ShowAlias(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if not self.original_command:
            self._log("No command provided for showing aliases.")
            return "No command provided for showing aliases."

        return self._show_alias()

    def _show_alias(self):
        alias_command = self.memdb.alias_command
        if not alias_command:
            self._log("No aliases set.")
            return "No aliases set."

        alias_list = [f"{alias}: {command}" for alias, command in alias_command.items()]
        return "\n".join(alias_list)

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)