from command.command import Command

class Commit(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        try:
            if self.memdb.in_transaction:
                self.memdb.in_transaction = False
                self.memdb.transaction_commands.append(self.original_command)
                self.memdb.org_data = {}
                for command in self.memdb.transaction_commands:
                    self.persistence_manager.append_AOF(command)
                self.memdb.transaction_commands.clear()
                return "Transaction committed successfully."
            else:
                raise Exception("No transaction in progress to commit.")
        except Exception as e:
            return f"Error committing transaction: {str(e)}"
        finally:
            if self.memdb.lock.locked():
                self.memdb.lock.release()