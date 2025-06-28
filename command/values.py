from command.command import Command

from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE


@register_command("values")
class Values(Command):
    def __init__(self, original_command=None):
        super().__init__()
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        values = []
        if self.memdb.in_load:
            values = self._execute_values()

        if memdb.in_transaction:
            values = self._execute_values()
        else:
            with self.memdb.lock:
                values = self._execute_values()
        return Response(
            status_code=STATUS_CODE["OK"],
            message="Values retrieved successfully.",
            data=values
        )
    def _execute_values(self):
        self.memdb.clean_expired_keys()
        values = [value["value"] for value in self.memdb.data.values() if "value" in value]
        if not values:
            return []
        else:
            return values
