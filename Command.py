from MemDB import inMemoryDB
from SysLog import logger

class command:
    def __init__(self):
        self.memdb = inMemoryDB()
        self.logger = logger(self.__class__.__name__)
        self.logger.log("Command interface initialized")

    def execute(self, cmd):
        parts = cmd.split()
        if not parts:
            return "No command provided"

        action = parts[0].lower()
        if action == "put" and len(parts) == 3:
            self.memdb.put(parts[1], parts[2], None)
            return self.return_msg(f"Stored {parts[1]}: {parts[2]}")
        
        elif action == "put" and len(parts) == 4:
            try:
                expiration_time = int(parts[3])
                self.memdb.put(parts[1], parts[2], expiration_time)
                return self.return_msg(f"Stored {parts[1]}: {parts[2]} with expiration time of {expiration_time} seconds")
            except ValueError:
                return self.return_msg("Invalid expiration time, must be an integer")
        
        elif action == "get" and len(parts) == 2:
            value = self.memdb.get(parts[1])
            return self.return_msg(f"{parts[1]}: {value}" if value is not None else f"{parts[1]} not found")
        
        elif action == "delete" and len(parts) == 2:
            self.memdb.delete(parts[1])
            return self.return_msg(f"Deleted {parts[1]}")
        
        elif action == "clear":
            self.memdb.clear()
            return self.return_msg("Cleared all data")
        
        elif action == "exists" and len(parts) == 2:
            exists = self.memdb.exists(parts[1])
            return self.return_msg(f"{parts[1]} exists: {exists}")
        
        elif action == "keys":
            return self.return_msg(f"Keys: {self.memdb.keys()}")
        elif action == "values":
            return self.return_msg(f"Values: {self.memdb.values()}")
        elif action == "items":
            return self.return_msg(f"Items: {self.memdb.items()}")
        elif action == "size":
            return self.return_msg(f"Size: {self.memdb.size()}")
        elif action == "help":
            return self.memdb.help()
        elif action == "begin":
            self.memdb.begin_transaction()
            return self.return_msg("Transaction started")
        elif action == "commit":
            self.memdb.commit_transaction()
            return self.return_msg("Transaction committed")
        elif action == "rollback":
            self.memdb.rollback_transaction()
            return self.return_msg("Transaction rolled back")
        else:
            return self.return_msg("Unknown command. Type 'help' for a list of commands.")
    
    def return_msg(self, msg):
        self.logger.log(msg)

    def run(self):
        print("Welcome to the in-memory database command interface!")
        print("Type 'help' for a list of commands.")
        while True:
            cmd = input("Enter command: ")
            if cmd.lower() == "exit":
                print("Exiting...")
                break
            self.execute(cmd)