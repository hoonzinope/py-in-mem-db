from command.command import Command
import time

from command.registry import register_command


@register_command("get")
class Get(Command):
    def __init__(self, key, original_command=None):
        super().__init__()
        self.key = key
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            return self._execute_get(self.key)

        if memdb.in_transaction:
            return self._execute_get(self.key)
        else:
            with self.memdb.lock:
                return self._execute_get(self.key)

    def _execute_get(self, key):
        if key in self.memdb.data:
            if self.memdb.data[key].get("expiration_time") is not None:
                if self.memdb.data[key]["expiration_time"] < time.time():
                    del self.memdb.data[key]
                    return None
                else:
                    return self.memdb.data[key]["value"]
            else:
                return self.memdb.data[key]["value"]
        else:
            return None