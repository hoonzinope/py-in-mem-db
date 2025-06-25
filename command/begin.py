from command.command import Command
import copy
from command.registry import register_command

@register_command("begin")
class Begin(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager
        if self.memdb.in_load:
            # If loading data, we should not start a transaction
            return
        if self.memdb.in_transaction:
            # If already in a transaction, just append the command
            pass
        else:
            # Start a new transaction
            self.memdb.lock.acquire()
            self.memdb.in_transaction = True
            self.memdb.transaction_commands = [self.original_command]
            self.memdb.org_data = copy.deepcopy(self.memdb.data)