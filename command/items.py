from command.command import Command
from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE
import time

@register_command("items")
class Items(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        result = None
        if self.memdb.in_load:
            self._log("Executing items command during load.")
            result = self._execute_items()

        if session_id not in self.memdb.in_tx:
            with self.memdb.lock:
                self._log("Executing items command with lock.")
                result = self._execute_items()
        else:
            self.memdb.tx_commands[session_id].append(self.original_command)
            result = self._execute_items_in_transaction(session_id)

        return Response(
            status_code=STATUS_CODE["OK"],
            message="Items retrieved successfully.",
            data=result
        )

    def _execute_items(self):
        self.memdb.clean_expired_keys()
        items = [(key, value["value"]) for key, value in self.memdb.data.items() if "value" in value]
        if not items:
            return []
        else:
            return items

    def _execute_items_in_transaction(self, session_id):
        copy = self.memdb.tx_data[session_id]["copy"]
        snapshot = self.memdb.tx_data[session_id]["snapshot"]

        result = []
        for key, value in snapshot.items():
            if key not in copy:
                if value['expiration_time'] is None or value['expiration_time'] > time.time():
                    copy[key] = value
                    result.append((key, copy[key]['value']))
            else:
                if copy[key]["expiration_time"] is None or copy[key]["expiration_time"] > time.time():
                    result.append((key, copy[key]["value"]))
                else:
                    del copy[key]
        return result

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)