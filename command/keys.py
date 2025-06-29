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

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        result = []
        if self.memdb.in_load:
            result = self._execute_keys()

        if session_id not in self.memdb.in_tx:
            with self.memdb.lock:
                result = self._execute_keys()
        else:
            self.memdb.tx_commands[session_id].append(self.original_command)
            result = self._execute_keys_in_transaction(session_id)

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

    def _execute_keys_in_transaction(self, session_id):
        copy = self.memdb.tx_data[session_id]["copy"]
        snapshot = self.memdb.tx_data[session_id]["snapshot"]

        result = []
        for key in snapshot:
            if key not in copy:
                if snapshot[key]['expiration_time'] is None or snapshot[key]['expiration_time'] > time.time():
                    copy[key] = snapshot[key]
                    result.append(key)
            else:
                if copy[key]["expiration_time"] is None or copy[key]["expiration_time"] > time.time():
                    result.append(key)
                else:
                    del copy[key]
        return result