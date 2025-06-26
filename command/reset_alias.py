from command.command import Command
from command.registry import register_command

@register_command("reset-alias")
class ResetAlias(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if not self.original_command:
            return "No command provided for resetting aliases."

        response = self._reset_alias()
        if self.persistence_manager:
            self.persistence_manager.save_alias(self.memdb.alias_command)
        return response

    def _reset_alias(self):
        # Clear the alias command dictionary
        self.memdb.alias_command.clear()
        return "All aliases have been reset."