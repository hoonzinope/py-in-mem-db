from command.command import Command
import time

from command.registry import register_command


@register_command("items")
class Items(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            return self._execute_items()

        if memdb.in_transaction:
            return self._execute_items()
        else:
            with self.memdb.lock:
                return self._execute_items()
            
    def _execute_items(self):
        self.memdb.clean_expired_keys()
        items = [(key, value["value"]) for key, value in self.memdb.data.items() if "value" in value]
        if not items:
            return []
        else:
            return items
