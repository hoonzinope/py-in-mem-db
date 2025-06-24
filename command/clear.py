from command.command import Command

class Clear(Command):
    def __init__(self, original_command: str = None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            return self._execute_clear()
        else:
            with self.memdb.lock:
                self.persistence_manager.append_AOF(self.original_command)
                return self._execute_clear()
            
    def _execute_clear(self):
        self.memdb.data.clear()