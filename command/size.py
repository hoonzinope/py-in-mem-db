from command.command import Command
import time

from command.registry import register_command


@register_command("size")
class Size(Command):
    def __init__(self, original_command: str = None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager
        if self.memdb.in_load:
            return self._execute_size()

        if memdb.in_transaction:
            return self._execute_size()
        else:
            with self.memdb.lock:
                return self._execute_size()
    
    def _execute_size(self):
        self.memdb.clean_expired_keys()
        size = len(self.memdb.data)
        return size