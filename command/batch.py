from command.command import Command
from command.registry import register_command, parse_command
from logger import Logger
from response import Response, STATUS_CODE
import shlex

@register_command("batch")
class Batch(Command):
    def __init__(self, commands):
        super().__init__()
        self.commands = commands
        self.results = []
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            raise RuntimeError("Cannot execute batch command during load operation")

        if session_id not in self.memdb.in_tx:
            # If not in transaction, we need to lock the database
            with self.memdb.lock:
                self._log("Executing batch command with lock")
                result = self._execute_batch_not_in_transaction(self.commands, session_id)
                return Response(
                    status_code=STATUS_CODE["OK"],
                    message="Batch command executed successfully",
                    data=result
                )
        else:
            result = self._execute_batch_in_transaction(self.commands)
            return Response(
                status_code=STATUS_CODE["OK"],
                message="Batch command executed successfully in transaction",
                data=result
            )

    # Execute the batch command in the context of a transaction
    def _execute_batch_in_transaction(self, commands):
        parsed_commands = self._convert_batch_to_commands(commands)
        try:
            for cmd in parsed_commands:
                if cmd:
                    result = self.memdb.execute(parse_command(cmd))
                    self.results.append(result.data)
        except Exception as e:
            # If an error occurs, rollback the transaction
            self.memdb.execute(parse_command("rollback"))
            self._log("Error executing batch command:", e)
            return []

        return self.results

    # Execute the batch command in the context of a lock
    def _execute_batch_not_in_transaction(self, commands, session_id):
        parsed_commands = self._convert_batch_to_commands(commands)
        self.memdb.execute(parse_command("begin"), session_id=session_id)
        try:
            for cmd in parsed_commands:
                if cmd:
                    result = self.memdb.execute(parse_command(cmd), session_id=session_id)
                    self.results.append(result.data)
        except Exception as e:
            # If an error occurs, rollback the transaction
            self.memdb.execute(parse_command("rollback"))
            self._log(f"Error executing batch command:{e}")
            return []

        self.memdb.execute(parse_command("commit"), session_id=session_id)
        return self.results

    # Convert the batch command string into a list of individual commands
    # this method ignores 'begin', 'commit', and 'rollback' commands
    # input example : -c "put \"key1\" \"value1\" 10000; put key2 value2 10000; begin; put key3 value3 10000; commit;"
    # output example: ['put "key1" "value1"', 'put key2 value2', 'put key3 value3']
    def _convert_batch_to_commands(self, commands):
        if not commands:
            return []
        tokens = shlex.split(commands.strip())
        if not tokens:
            return []  # Return an empty list if tokens is empty
        input_type = tokens[0]
        if input_type == "-c" or input_type == "--command":
            if len(tokens) < 2:  # Ensure there are enough tokens
                return []  # Return an empty list if insufficient tokens
            commands = " ".join(tokens[1:])
        elif input_type == "-f" or input_type == "--file":
            if len(tokens) < 2:  # Ensure there are enough tokens
                return []  # Return an empty list if insufficient tokens
            input_file_path = tokens[1]
            with open(input_file_path, 'r') as file:
                commands = file.read()
        else: # default type is -c
            if len(tokens) < 2:  # Ensure there are enough tokens
                return []  # Return an empty list if insufficient tokens
            commands = " ".join(tokens[1:])

        command_list = []
        for cmd in commands.strip().split(';'):
            cmd = cmd.strip()
            if cmd:
                if cmd in ('begin', 'commit', 'rollback'):
                    continue
                else:
                    command_list.append(cmd)
        return command_list

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)
