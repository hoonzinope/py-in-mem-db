from command.command import Command
from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE

@register_command("commit")
class Commit(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
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
                if self.memdb.in_transaction:
                    self.memdb.in_transaction = False
                    self.memdb.transaction_commands.append(self.original_command)
                    self.memdb.org_data = {}
                    for command in self.memdb.transaction_commands:
                        self.persistence_manager.append_aof(command)
                    self.memdb.transaction_commands.clear()
                    self._log("Transaction committed successfully.")
                    return Response(
                        status_code=STATUS_CODE["OK"],
                        message="Transaction committed successfully.",
                        data=None
                    )
                else:
                    raise Exception("No transaction in progress to commit.")
            except Exception as e:
                self._log( f"Error committing transaction: {str(e)}" )
                return Response(
                    status_code=STATUS_CODE["INTERNAL_SERVER_ERROR"],
                    message=f"Error committing transaction: {str(e)}",
                    data=None
                )
            finally:
                if self.memdb.lock.locked():
                    self.memdb.lock.release()

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)
