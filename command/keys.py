from command.command import Command
import time

from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE


@register_command("keys")
class Keys(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        result = []
        if self.memdb.in_load:
            result = self._execute_keys()

        if memdb.in_transaction:
            result = self._execute_keys()
        else:
            with self.memdb.lock:
                result = self._execute_keys()
        return Response(
            status_code=STATUS_CODE["OK"],
            message="Keys retrieved successfully.",
            data=result
        )
    def _execute_keys(self):
        self.memdb.clean_expired_keys()
        keys = list(self.memdb.data.keys())
        if not keys:
            return []
        else:
            return keys