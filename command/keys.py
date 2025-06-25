from command.command import Command
import time

from command.registry import register_command


@register_command("keys")
class Keys(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            return self._execute_keys()

        if memdb.in_transaction:
            return self._execute_keys()
        else:
            with self.memdb.lock:
                return self._execute_keys()
            
    def _execute_keys(self):
        self.memdb.clean_expired_keys()
        keys = list(self.memdb.data.keys())
        if not keys:
            return []
        else:
            return keys