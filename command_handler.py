from memory_store import inMemoryDB
from logger import logger
from command_parser import CommandParser

class command:
    def __init__(self):
        self.logger = logger(self.__class__.__name__)
        self.logger.log("Command interface initialized")
        self.parser = CommandParser()
        self.memdb = inMemoryDB()

    def execute(self, cmd):
        command_obj = self.parser.parse(cmd)
        if command_obj is None:
            self.return_msg("Invalid command. Type 'help' for a list of commands.")
            return
        else:
            return self.memdb.execute(command_obj)

    def return_msg(self, msg):
        self.logger.log(msg)

    def run(self):
        print("Welcome to the in-memory database command interface!")
        print("Type 'help' for a list of commands.")
        while True:
            cmd = input("cmd>> ")
            if cmd.lower() == "exit":
                print("Exiting...")
                break
            self.execute(cmd)