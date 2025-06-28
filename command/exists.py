from command.command import Command
import time

from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE


@register_command("exists")
class Exists(Command):
    def __init__(self, key, original_command=None):
        super().__init__()
        self.key = key
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        result = True
        if self.memdb.in_load:
            result = self._execute_exists(self.key)

        if memdb.in_transaction:
            result = self._execute_exists(self.key)
        else:
            with self.memdb.lock:
                result = self._execute_exists(self.key)

        return Response(
            status_code=STATUS_CODE["OK"],
            message=f"Key '{self.key}' exists: {result}",
            data=result
        )

    def _execute_exists(self, key):
        if key not in self.memdb.data:
            self._log(f"Key '{key}' does not exist.")
            return False

        if self.memdb.data[key].get("expiration_time") is None:
            self._log(f"Key '{key}' exists without expiration.")
            return True

        if self.memdb.data[key]["expiration_time"] > time.time():
            self._log(f"Key '{key}' exists and has not expired.")
            return True
        else:
            del self.memdb.data[key]
            self._log(f"Key '{key}' exists but has expired.")
            return False

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)