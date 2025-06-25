from command.command import Command
from command.registry import register_command, parse_command


@register_command("batch")
class Batch(Command):
    def __init__(self, commands):
        super().__init__()
        self.commands = commands
        self.results = []

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            raise RuntimeError("Cannot execute batch command during load operation")

        if self.memdb.in_transaction:
            print("Executing batch command in transaction mode")
            return self._execute_batch_in_transaction(self.commands)
        else:
            print("Executing batch command not in transaction mode")
            return self._execute_batch_not_in_transaction(self.commands)

    # Execute the batch command in the context of a transaction
    def _execute_batch_in_transaction(self, commands):
        parsed_commands = self._convert_batch_to_commands(commands)
        try:
            for cmd in parsed_commands:
                if cmd:
                    result = self.memdb.execute(parse_command(cmd))
                    self.results.append(result)
        except Exception as e:
            # If an error occurs, rollback the transaction
            self.memdb.execute(parse_command("rollback"))
            print("Error executing batch command:", e)
            return []

        return self.results

    # Execute the batch command in the context of a lock
    def _execute_batch_not_in_transaction(self, commands):
        parsed_commands = self._convert_batch_to_commands(commands)
        self.memdb.execute(parse_command("begin"))
        try:
            for cmd in parsed_commands:
                if cmd:
                    result = self.memdb.execute(parse_command(cmd))
                    self.results.append(result)
        except Exception as e:
            # If an error occurs, rollback the transaction
            self.memdb.execute(parse_command("rollback"))
            print("Error executing batch command:", e)
            return []

        self.memdb.execute(parse_command("commit"))
        return self.results


    def _convert_batch_to_commands(self, commands):
        command_list = []
        for cmd in commands.strip().split(';'):
            cmd = cmd.strip()
            if cmd:
                if cmd in ['begin', 'commit', 'rollback']:
                    continue
                else:
                    command_list.append(cmd)
        return command_list
