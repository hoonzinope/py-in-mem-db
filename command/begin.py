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

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager
        if self.memdb.in_load:
            # If loading data, we should not start a transaction
            self._log("Cannot start a transaction during load operation")
            pass

        if session_id not in self.memdb.in_tx:
            # Start a new transaction for the session
            self._log(f"Starting a new transaction for session {session_id}")
            self.memdb.in_tx[session_id] = True
            self.memdb.tx_commands[session_id] = [self.original_command]
            self.memdb.tx_data[session_id] = {"copy": {}, "snapshot": {}}
            with self.memdb.lock:
                self.memdb.tx_data[session_id]["snapshot"] = copy.deepcopy(self.memdb.data)
        else:
            # If already in a transaction for this session, just append the command
            self._log(f"Appending command to existing transaction for session {session_id}")

        return Response(
            status_code=STATUS_CODE["OK"],
            message="Transaction started successfully",
            data=None
        )

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)
