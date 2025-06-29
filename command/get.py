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

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            self._log(f"Executing get for key: {self.key} during load.")
            return Response(
                status_code=STATUS_CODE["OK"],
                message=f"Key '{self.key}' retrieved during load.",
                data=self._execute_get(self.key)
            )

        if session_id not in self.memdb.in_tx:
            with self.memdb.lock:
                self._log(f"Executing get for key: {self.key} lock.")
                return Response(
                    status_code=STATUS_CODE["OK"],
                    message=f"Key '{self.key}' retrieved.",
                    data=self._execute_get(self.key)
                )
        else:
            self.memdb.tx_commands[session_id].append(self.original_command)
            return self._execute_get_in_transaction(self.key, session_id)

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

    def _execute_get_in_transaction(self, key, session_id):
        copy = self.memdb.tx_commands[session_id]["copy"]
        snapshot = self.memdb.tx_commands[session_id]["snapshot"]
        if self.key in copy:
            if copy[self.key]["expiration_time"] is None or copy[self.key]["expiration_time"] > time.time():
                return Response(
                    status_code=STATUS_CODE["OK"],
                    message=f"Key '{self.key}' retrieved during transaction.",
                    data=copy[self.key]["value"]
                )
            else:
                del copy[self.key]
                return Response(
                    status_code=STATUS_CODE["NOT_FOUND"],
                    message=f"Key '{self.key}' has expired during transaction.",
                    data=None
                )
        elif self.key in snapshot:
            if snapshot[self.key]["expiration_time"] is None or snapshot[self.key]["expiration_time"] > time.time():
                return Response(
                    status_code=STATUS_CODE["OK"],
                    message=f"Key '{self.key}' retrieved during transaction.",
                    data=snapshot[self.key]["value"]
                )
            else:
                return Response(
                    status_code=STATUS_CODE["NOT_FOUND"],
                    message=f"Key '{self.key}' has expired during transaction.",
                    data=None
                )
        else:
            self._log(f"Key '{self.key}' not found during transaction.")
            # Key not found in transaction, return None
            return Response(
                status_code=STATUS_CODE["NOT_FOUND"],
                message=f"Key '{self.key}' not found during transaction.",
                data=None
            )

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)