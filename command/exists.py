from command.command import Command
import time

class Exists(Command):
    def __init__(self, key, original_command=None):
        super().__init__()
        self.key = key
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            return self._execute_exists(self.key)
        else:
            with self.memdb.lock:
                self.persistence_manager.append_AOF(self.original_command)
                return self._execute_exists(self.key)
            
    def _execute_exists(self, key):
        if key in self.memdb.data:
            if self.memdb.data[key].get("expiration_time") is not None:
                if self.memdb.data[key]["expiration_time"] < time.time():
                    del self.memdb.data[key]
                    return False
                else:
                    return True
            else:
                return True
        else:
            return False