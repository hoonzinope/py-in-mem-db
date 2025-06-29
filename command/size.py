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

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager
        size = 0
        if self.memdb.in_load:
            size = self._execute_size()

        if session_id not in self.memdb.in_tx:
            # If not in transaction, we need to lock the database
            with self.memdb.lock:
                size = self._execute_size()
        else:
            # If in transaction, we can append the command to the transaction list
            self.memdb.tx_commands[session_id].append(self.original_command)
            size = self._execute_size_in_transaction(session_id)
            return Response(
                status_code=STATUS_CODE["OK"],
                message=f"Current size of the database in transaction: {size}",
                data=size
            )

        return Response(
            status_code=STATUS_CODE["OK"],
            message=f"Current size of the database: {size}",
            data=size
        )

    def _execute_size(self):
        self.memdb.clean_expired_keys()
        size = len(self.memdb.data)
        return size

    def _execute_size_in_transaction(self, session_id):
        copy = self.memdb.tx_data[session_id]["copy"]
        snapshot = self.memdb.tx_data[session_id]["snapshot"]
        size = 0
        for key in snapshot:
            if key not in copy:
                if snapshot[key]['expiration_time'] is None or snapshot[key]['expiration_time'] > time.time():
                    size += 1
            else:
                if copy[key]["expiration_time"] is None or copy[key]["expiration_time"] > time.time():
                    size += 1
                else:
                    del copy[key]
        return size

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)