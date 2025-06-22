from MemDB import inMemoryDB

class command:
    def __init__(self):
        self.memdb = inMemoryDB()

    def execute(self, cmd):
        parts = cmd.split()
        if not parts:
            return "No command provided"

        action = parts[0].lower()
        if action == "put" and len(parts) == 3:
            self.memdb.put(parts[1], parts[2])
            return f"Stored {parts[1]}: {parts[2]}"
        elif action == "get" and len(parts) == 2:
            value = self.memdb.get(parts[1])
            return f"{parts[1]}: {value}" if value is not None else f"{parts[1]} not found"
        elif action == "delete" and len(parts) == 2:
            self.memdb.delete(parts[1])
            return f"Deleted {parts[1]}"
        elif action == "clear":
            self.memdb.clear()
            return "Database cleared"
        elif action == "exists" and len(parts) == 2:
            exists = self.memdb.exists(parts[1])
            return f"{parts[1]} exists: {exists}"
        elif action == "keys":
            return f"Keys: {self.memdb.keys()}"
        elif action == "values":
            return f"Values: {self.memdb.values()}"
        elif action == "items":
            return f"Items: {self.memdb.items()}"
        elif action == "size":
            return f"Size: {self.memdb.size()}"
        elif action == "help":
            return self.memdb.help()
        else:
            return "Invalid command"
        
    def run(self):
        print("Welcome to the in-memory database command interface!")
        print("Type 'help' for a list of commands.")
        while True:
            cmd = input("Enter command: ")
            if cmd.lower() == "exit":
                print("Exiting...")
                break
            response = self.execute(cmd)
            print(response)

if __name__ == "__main__":
    cmd = command()
    cmd.run()
