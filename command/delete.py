from command.command import Command
from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE


@register_command("delete")
class Delete(Command):
    def __init__(self, key, original_command):
        super().__init__()
        self.key = key
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            self._execute_delete(self.key)

        if session_id not in self.memdb.in_tx:
            with self.memdb.lock:
                self.persistence_manager.append_aof(self.original_command)
                self._execute_delete(self.key)
        else:
            self.memdb.tx_commands[session_id].append(self.original_command)
            del self.memdb.tx_data[session_id]["copy"][self.key]

        return Response(
            status_code=STATUS_CODE["OK"],
            message=f"Key '{self.key}' deleted successfully.",
            data=None
        )
            
    def _execute_delete(self, key: str):
        if key in self.memdb.data:
            del self.memdb.data[key]