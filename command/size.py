from command.command import Command
import time

from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE


@register_command("size")
class Size(Command):
    def __init__(self, original_command: str = None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager
        size = 0
        if self.memdb.in_load:
            size = self._execute_size()

        if memdb.in_transaction:
            size = self._execute_size()
        else:
            with self.memdb.lock:
                size = self._execute_size()

        return Response(
            status_code=STATUS_CODE["OK"],
            message=f"Current size of the database: {size}",
            data=size
        )

    def _execute_size(self):
        self.memdb.clean_expired_keys()
        size = len(self.memdb.data)
        return size

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)