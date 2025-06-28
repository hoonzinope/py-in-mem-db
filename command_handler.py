from memory_store import inMemoryDB
from logger import Logger
from command_parser import Parser
from response import Response, STATUS_CODE
import shlex
import readline

class Command:
    def __init__(self):
        self.logger = Logger.get_logger()
        self.log("Command interface initialized")
        self.memdb = inMemoryDB.get_instance()
        self.command_parser = Parser()

        self.execute("load")  # Load initial data if available
        self.alias_command = self.memdb.alias_command

    def execute(self, cmd) -> Response:
        cmd = self.convert_alias(cmd) if cmd != "load" else cmd
        command_obj = self.command_parser.parse(cmd)
        if command_obj is None:
            msg = "Invalid command. Type 'help' for a list of commands."
            self.log(msg)
            return Response(
                status_code=STATUS_CODE["BAD_REQUEST"],
                message=msg,
                data=None
            )
        else:
            return self.memdb.execute(command_obj)

    def convert_alias(self, cmd):
        parts = shlex.split(cmd)
        if len(parts) < 2:
            if parts[0] in self.alias_command:
                return self.alias_command[parts[0]]
            else:
                return cmd

        alias = parts[0]
        if alias in self.alias_command:
            command = self.alias_command[alias]
            return command + " " + " ".join(parts[1:])

        return cmd  # No alias found, return original command

    # run method to start the command interface (only for testing purposes)
    def run(self):
        self.log("Welcome to the in-memory database command interface!")
        self.log("Type 'help' for a list of commands.")
        while True:
            cmd = input("cmd>> ")
            if cmd.lower() == "exit" or cmd.lower() == "quit":
                self.log("Exiting...")
                self.logger.close()
                break
            elif cmd.strip() == "":
                continue
            elif cmd.lower() == "load":
                self.log("Load command should not be executed directly.")
                continue
            response = self.execute(cmd)
            if response is not None:
                print(response)

    def log(self, message):
        self.logger.log(message, name=self.__class__.__name__)