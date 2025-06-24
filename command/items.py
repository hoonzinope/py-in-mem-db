from command.command import Command
import time

class Items(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            return self._execute_items()
        else:
            with self.memdb.lock:
                self.persistence_manager.append_AOF(self.original_command)
                return self._execute_items()
            
    def _execute_items(self):
        self.memdb._clean_expired_keys()
        items = [(key, value["value"]) for key, value in self.memdb.data.items() if "value" in value]
        if not items:
            return []
        else:
            return items
