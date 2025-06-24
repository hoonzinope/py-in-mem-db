from command.command import Command
import time

class Keys(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            return self._execute_keys()
        else:
            with self.memdb.lock:
                self.persistence_manager.append_AOF(self.original_command)
                return self._execute_keys()
            
    def _execute_keys(self):
        self.memdb._clean_expired_keys()
        keys = list(self.memdb.data.keys())
        if not keys:
            return []
        else:
            return keys