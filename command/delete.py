from command.command import Command

class Delete(Command):
    def __init__(self, key: str, original_command: str = None):
        super().__init__()
        self.key = key
        self.original_command = original_command

    def execute(self, db):
        self.memdb = db.memdb
        self.persistence_manager = db.persistence_manager

        if self.memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            return self._execute_delete(self.key)
        else:
            with self.memdb.lock:
                self.persistence_manager.append_AOF(self.original_command)
                return self._execute_delete(self.key)
            
    def _execute_delete(self, key: str):
        if key in self.memdb.data:
            del self.memdb.data[key]