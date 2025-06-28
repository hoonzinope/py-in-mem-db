from command.command import Command
import copy
from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE

@register_command("rollback")
class Rollback(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager
        if self.memdb.in_load:
            return Response(
                status_code=STATUS_CODE["OK"],
                message="Rollback executed during load, no changes made.",
                data=None
            )

        try:
            if self.memdb.in_transaction:
                self.memdb.data = copy.deepcopy(self.memdb.org_data)
                self.memdb.in_transaction = False
                self.memdb.transaction_commands = []
                self.memdb.org_data = {}
                self._log("Transaction rolled back successfully.")
                return Response(
                    status_code=STATUS_CODE["OK"],
                    message="Transaction rolled back successfully.",
                    data=None
                )
            else:
                self._log("No transaction in progress to roll back.")
                raise Exception("No transaction in progress to roll back.")
        except Exception as e:
            self._log(f"Rollback failed: {str(e)}")
            return Response(
                status_code=STATUS_CODE["INTERNAL_SERVER_ERROR"],
                message=f"Rollback failed: {str(e)}",
                data=None
            )
        finally:
            if self.memdb.lock.locked():
                self.memdb.lock.release()

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)