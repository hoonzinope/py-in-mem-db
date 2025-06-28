from command.command import Command
from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE

@register_command("reset-alias")
class ResetAlias(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if not self.original_command:
            msg = "No command provided for resetting aliases."
            self._log(msg)
            return Response(
                status_code=STATUS_CODE["BAD_REQUEST"],
                message=msg,
                data=None
            )

        response = self._reset_alias()
        if self.persistence_manager:
            self.persistence_manager.save_alias(self.memdb.alias_command)
        return Response(
            status_code=STATUS_CODE["OK"],
            message=response,
            data=None
        )

    def _reset_alias(self):
        # Clear the alias command dictionary
        self.memdb.alias_command.clear()
        self._log("All aliases have been reset.")
        return "All aliases have been reset."

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)