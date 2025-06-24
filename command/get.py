from command.command import Command
import time

class Get(Command):
    def __init__(self, key, original_command=None):
        super().__init__()
        self.key = key
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            return self._execute_get(self.key)
        else:
            with self.memdb.lock:
                self.persistence_manager.append_AOF(self.original_command)
                return self._execute_get(self.key)

    def _execute_get(self, key):
        if key in self.memdb.data:
            if self.memdb.data[key].get("expiration_time") is not None:
                if self.memdb.data[key]["expiration_time"] < time.time():
                    del self.memdb.data[key]
                    self.logger.log(f"Key {key} has expired and was deleted")
                    return None
                else:
                    return self.memdb.data[key]["value"]
            else:
                return self.memdb.data[key]["value"]
        else:
            self.logger.log(f"Key {key} not found")
            return None