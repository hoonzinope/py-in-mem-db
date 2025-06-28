from command.command import Command
from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE

@register_command("items")
class Items(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        result = ""
        if self.memdb.in_load:
            self._log("Executing items command during load.")
            result = self._execute_items()

        if memdb.in_transaction:
            self._log("Executing items command during transaction.")
            result = self._execute_items()
        else:
            with self.memdb.lock:
                self._log("Executing items command with lock.")
                result = self._execute_items()

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

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)