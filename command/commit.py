from command.command import Command
from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE
import time

@register_command("commit")
class Commit(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager
        if self.memdb.in_load:
            return Response(
                status_code=STATUS_CODE["BAD_REQUEST"],
                message="Cannot commit during load operation.",
                data=None
            )
        else:
            try:
                if session_id in self.memdb.in_tx:
                    self._commit(session_id)
                    return Response(
                        status_code=STATUS_CODE["OK"],
                        message="Transaction committed successfully.",
                        data=None
                    )
                else:
                    raise Exception("No transaction in progress to commit.")
            except Exception as e:
                self._log( f"Error committing transaction: {str(e)}" )
                self._reject_commit(session_id)
                return Response(
                    status_code=STATUS_CODE["INTERNAL_SERVER_ERROR"],
                    message=f"Error committing transaction: {str(e)}",
                    data=None
                )

    def _commit(self, session_id):
        if session_id in self.memdb.in_tx:
            # check snapshot == self.memdb.data
            snapshot = self.memdb.tx_data[session_id]["snapshot"]
            copy = self.memdb.tx_data[session_id]["copy"]

            for key, value in snapshot.items():
                if key not in self.memdb.data or self.memdb.data[key]['value'] != value['value'] or \
                    self.memdb.data[key]['expiration_time'] != value['expiration_time']:
                    self._log(f"Snapshot mismatch for key {key}. Cannot commit transaction.")
                    raise Exception("Snapshot mismatch. Cannot commit transaction.")
            # Commit the transaction
            with self.memdb.lock:
                for key, value in copy.items():
                    if value["expiration_time"] is None or value["expiration_time"] > time.time():
                        self.memdb.data[key] = value

            # append the commands to AOF
            for command in self.memdb.tx_commands[session_id]:
                self.persistence_manager.append_aof(command)

            # Clear the transaction data
            del self.memdb.in_tx[session_id]
            del self.memdb.tx_data[session_id]
            del self.memdb.tx_commands[session_id]
            self._log(f"Transaction for session {session_id} committed successfully.")
        else:
            self._log(f"No transaction found for session {session_id} to commit.")

    def _reject_commit(self, session_id):
        if session_id in self.memdb.in_tx:
            # Clear the transaction data without committing
            del self.memdb.in_tx[session_id]
            del self.memdb.tx_data[session_id]
            del self.memdb.tx_commands[session_id]
            self._log(f"Transaction for session {session_id} rejected and cleared.")
        else:
            self._log(f"No transaction found for session {session_id} to reject.")

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)
