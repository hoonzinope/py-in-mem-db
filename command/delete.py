from command.command import Command
from command.registry import register_command


@register_command("delete")
class Delete(Command):
    def __init__(self, key, original_command):
        super().__init__()
        self.key = key
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            return self._execute_delete(self.key)

        if self.memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            return self._execute_delete(self.key)
        else:
            with self.memdb.lock:
                self.persistence_manager.append_aof(self.original_command)
                return self._execute_delete(self.key)
            
    def _execute_delete(self, key: str):
        if key in self.memdb.data:
            del self.memdb.data[key]