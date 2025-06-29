import copy

from command.command import Command
from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE

@register_command("clear")
class Clear(Command):
    def __init__(self, original_command: str = None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            self._execute_clear()

        if session_id not in self.memdb.in_tx:
            with self.memdb.lock:
                self.persistence_manager.append_aof(self.original_command)
                self._execute_clear()
        else:
            self.memdb.tx_commands[session_id].append(self.original_command)
            self._execute_clear_in_transaction(session_id)

        return Response(
            status_code=STATUS_CODE["OK"],
            message="Database cleared successfully",
            data=None
        )
            
    def _execute_clear(self):
        self.memdb.data.clear()

    def _execute_clear_in_transaction(self, session_id):
        self.memdb.tx_data[session_id]["copy"].clear()