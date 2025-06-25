from command.command import Command
import copy

from command.registry import register_command


@register_command("rollback")
class Rollback(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager
        if self.memdb.in_load:
            return
        try:
            if self.memdb.in_transaction:
                self.memdb.data = copy.deepcopy(self.memdb.org_data)
                self.memdb.in_transaction = False
                self.memdb.transaction_commands = []
                self.memdb.org_data = {}
            else:
                raise Exception("No transaction in progress to roll back.") 
        finally:    
            if self.memdb.lock.locked():
                self.memdb.lock.release()