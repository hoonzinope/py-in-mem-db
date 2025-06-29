from command.command import Command

from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE
import time


@register_command("values")
class Values(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        values = []
        if self.memdb.in_load:
            values = self._execute_values()

        if session_id not in self.memdb.in_tx:
            # If not in transaction, we need to lock the database
            with self.memdb.lock:
                values = self._execute_values()
        else:
            # If in transaction, we can append the command to the transaction list
            self.memdb.tx_commands[session_id].append(self.original_command)
            values = self._execute_values_in_transaction(session_id)

        return Response(
            status_code=STATUS_CODE["OK"],
            message="Values retrieved successfully during transaction.",
            data=values
        )

    def _execute_values(self):
        self.memdb.clean_expired_keys()
        values = [value["value"] for value in self.memdb.data.values() if "value" in value]
        if not values:
            return []
        else:
            return values

    def _execute_values_in_transaction(self, session_id):
        copy = self.memdb.tx_data[session_id]["copy"]
        snapshot = self.memdb.tx_data[session_id]["snapshot"]

        values = []
        keyset = set(copy.keys()).union(snapshot.keys())
        for key in keyset:
            if key in copy:
                if copy[key]["expiration_time"] is None or copy[key]["expiration_time"] > time.time():
                    values.append(copy[key]["value"])
                else:
                    del copy[key]
            elif key in snapshot:
                if snapshot[key]["expiration_time"] is None or snapshot[key]["expiration_time"] > time.time():
                    values.append(snapshot[key]["value"])
        return values
