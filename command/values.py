from command.command import Command
import time

class Values(Command):
    def __init__(self, key, original_command=None):
        super().__init__()
        self.key = key
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            return self._execute_values()
        else:
            with self.memdb.lock:
                self.persistence_manager.append_AOF(self.original_command)
                return self._execute_values()
            
    def _execute_values(self):
        self.memdb._clean_expired_keys()
        values = [value["value"] for value in self.memdb.data.values() if "value" in value]
        if not values:
            return []
        else:
            return values
