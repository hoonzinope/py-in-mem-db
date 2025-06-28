from command.command import Command
import copy
from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE

@register_command("begin")
class Begin(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager
        if self.memdb.in_load:
            # If loading data, we should not start a transaction
            self._log("Cannot start a transaction during load operation")
            pass
        if self.memdb.in_transaction:
            # If already in a transaction, just append the command
            self._log("Cannot start a transaction during transaction operation")
            pass
        else:
            # Start a new transaction
            self._log("Starting a new transaction")
            self.memdb.lock.acquire()
            self.memdb.in_transaction = True
            self.memdb.transaction_commands = [self.original_command]
            self.memdb.org_data = copy.deepcopy(self.memdb.data)

        return Response(
            status_code=STATUS_CODE["OK"],
            message="Transaction started successfully",
            data=None
        )

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)
