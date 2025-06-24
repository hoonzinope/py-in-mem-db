from command.command import Command
import time

class Size(Command):
    def __init__(self, key: str, original_command: str = None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            return self._execute_size()
        else:
            with self.memdb.lock:
                self.persistence_manager.append_AOF(self.original_command)
                return self._execute_size()
    
    def _execute_size(self):
        self.memdb._clean_expired_keys()
        size = len(self.memdb.data)
        return size