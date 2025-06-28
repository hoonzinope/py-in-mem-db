from command.command import Command
import time

from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE


@register_command("get")
class Get(Command):
    def __init__(self, key, original_command=None):
        super().__init__()
        self.key = key
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            self._log(f"Executing get for key: {self.key} during load.")
            return Response(
                status_code=STATUS_CODE["OK"],
                message=f"Key '{self.key}' retrieved during load.",
                data=self._execute_get(self.key)
            )

        if memdb.in_transaction:
            self._log(f"Executing get for key: {self.key} during transaction.")
            return Response(
                status_code=STATUS_CODE["OK"],
                message=f"Key '{self.key}' retrieved during transaction.",
                data=self._execute_get(self.key)
            )
        else:
            with self.memdb.lock:
                self._log(f"Executing get for key: {self.key} lock.")
                return Response(
                    status_code=STATUS_CODE["OK"],
                    message=f"Key '{self.key}' retrieved.",
                    data=self._execute_get(self.key)
                )

    def _execute_get(self, key):
        if key not in self.memdb.data:
            return None

        if self.memdb.data[key].get("expiration_time") is None:
            return self.memdb.data[key]["value"]

        if self.memdb.data[key]["expiration_time"] < time.time():
            del self.memdb.data[key]
            return None
        else:
            return self.memdb.data[key]["value"]

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)