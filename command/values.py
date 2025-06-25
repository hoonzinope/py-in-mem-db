from command.command import Command
import time

from command.registry import register_command


@register_command("values")
class Values(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            return self._execute_values()

        if memdb.in_transaction:
            return self._execute_values()
        else:
            with self.memdb.lock:
                return self._execute_values()
            
    def _execute_values(self):
        self.memdb.clean_expired_keys()
        values = [value["value"] for value in self.memdb.data.values() if "value" in value]
        if not values:
            return []
        else:
            return values
