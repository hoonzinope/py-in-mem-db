# In-Memory Key-Value DB with Python

A simple in-memory key-value database implementation built with Python.

## Version

* Python 3.8 or higher

## Features

* Stores and retrieves data entirely in memory
* Manages data in a key-value format
* Supports CRUD operations (Create, Read, Update, Delete)
* Supports data expiration (TTL)

  * (checks on access: lazy expiration + periodic cleanup thread: active expiration)
* Ensures data consistency with lock-based concurrency control
* Supports transactions (begin, commit, rollback)
* Provides backup and restore functionality
* Supports alias commands
* Supports batch commands (execute multiple commands at once)
* Supports find command (search keys or values by pattern)
* Logging support via a dedicated logger class

  * Prints error logs
  * Records command logs in a background thread
* Implements a server-client architecture

  * Interacts with the database via command interface
  * Communicates with the client using the RESP protocol
* Provides a RESTful API via HTTP server

  * Communicates using JSON format
* Pure Python implementation with no external dependencies

#### TTL (Expiration) Feature

* Each data item can have a TTL (Time-To-Live).
* Two expiration mechanisms are implemented:

  * **Lazy expiration**: On each access (e.g., get), checks if the data has expired. If expired, automatically deletes and returns `None`.
  * **Active expiration**: A separate background thread periodically scans and deletes expired data.
* This ensures expired data is cleaned up either immediately or periodically.

#### Lock-based Concurrency Control

* Uses a Lock class to handle concurrency issues.
* All data access is protected by locks to maintain consistency in multi-threaded environments.
* Locks are managed with `with` statements for automatic acquire and release.

#### Transaction Support

* The database supports transactions.
* Use `begin()`, `commit()`, and `rollback()` to manage transactions.
* All operations inside a transaction are only applied on `commit()`.
* Calling `rollback()` cancels all changes made within the transaction.

#### Backup & Restore

* The database state is periodically backed up in the background.

  * (Current state is stored in `./meta-data/snapshot.db`.)
* Changes are also logged in AOF (Append-Only File) format on each modification.

  * (Stored in `./meta-data/AOF.txt`.)
* On restart, the database restores state by loading `snapshot.db` and `AOF.txt`.

#### Alias Commands

* You can set aliases for frequently used commands.
* Alias information is saved to `./meta-data/alias.json` and auto-loaded on restart.
* Use `show-alias` to view the current list of aliases.
* Example usage:

```bash
cmd>> alias k keys
cmd>> k
['z', '2']
cmd>> alias i items
cmd>> i
[('z', '1'), ('2', '1')]
cmd>> show-alias
set: put
v: values
k: keys
i: items
cmd>> exit
Exiting...
```

#### Batch Commands

* Use the `batch` command to execute multiple commands at once.
* Separate commands with `;`. Commands can be on separate lines.
* Executes automatically in transaction mode: commits only if all commands succeed.
* Supported in both cmd mode and file mode.

  * Default is cmd mode.
  * Use `-c` or `--cmd` for command mode, `-f` or `--file` for file mode.
* Example:

```bash
cmd>> batch -c "put a 1 10000; put b 1 10000; get a; get b;"
Executing batch command not in transaction mode
[None, None, '1', '1']
cmd>> exit 
Exiting...
```

#### Find Command

* Use `find -[k,v] -[r,l] <search>` to search for keys or values by pattern.

  * `-k` or `--key` to search by key
  * `-v` or `--value` to search by value
  * `-l` or `--like` for wildcard pattern search
  * `-r` or `--regex` for regex pattern search
* Example:

```bash
cmd>> put a 1 10000
cmd>> put b 2 10000
cmd>> put c 1 10000
cmd>> items
[('a', '1'), ('b', '2'), ('c', '1')]
cmd>> find -k a
['a']
cmd>> find -k -l *
['a', 'b', 'c']
cmd>> exit
Exiting...
```

#### Server-Client Architecture

* Implements a server-client architecture to support multi-client environments.
* Run `/protocol/server.py` to start the server, and `/protocol/client.py` to connect as a client.
* The server communicates using the RESP protocol (`/protocol/codec.py`).
* Default server runs on `localhost:8080`.
* Supports transactions.

#### RESTful API via HTTP Server

* Run `/protocol/httpHandler.py` to start the HTTP server.
* The HTTP server exposes a RESTful API so clients can store and retrieve data via HTTP requests.
* API endpoints:

  * `get`

    * `GET /keys`: Returns all keys.
    * `GET /values`: Returns all values.
    * `GET /items`: Returns all key-value pairs.
    * `GET /size`: Returns the number of items in the database.
    * `GET /help`: Returns the list of available commands.
    * `GET /show-alias`: Returns the current alias list.
  * `post`

    * `POST /get`: Retrieves value by key. Automatically deletes expired data.
    * `POST /exists`: Checks if a key exists.
    * `POST /alias`: Sets an alias. Send alias data as JSON in request body.
    * `POST /find`: Searches for keys by pattern.
    * `POST /clear`: Deletes all data in the database.
  * `put`

    * `PUT /put`: Stores a value by key. Send data as JSON in request body.
    * `PUT /batch`: Executes multiple commands at once. Send commands as JSON list.
  * `delete`

    * `DELETE /delete`: Deletes a key-value pair.
    * `DELETE /reset-alias`: Resets all aliases.
* Default server runs on `localhost:8080`.
* All requests and responses use JSON format.
* Supports transactions.

  * Example request:

    ```http
    POST /put HTTP/1.1
    {
        "command": "a 10 10000"
    }
    ```
  * Example response:

    ```json
    {
        "received": {
            "command": "a 15 10000"
        },
        "status": 200,
        "message": "Key 'a' set with value '15' and expiration time '10000'",
        "data": null
    }
    ```

## Installation

```bash
git clone https://github.com/your-username/py-in-mem.git
cd py-in-mem
```

## Usage Example

```bash
$ > python main.py
[2025-06-25 13:43:45]   [Command]       log:Command interface initialized
[2025-06-25 13:43:45]   [inMemoryDB]    log:Initialized in-memory database
Welcome to the in-memory database command interface!
Type 'help' for a list of commands.
cmd>> keys
['a', 'b', 'c']
cmd>> delete c
Appending to AOF: delete c
cmd>> exists c
False
cmd>> exit 
Exiting...
```

## Server-Client Example

```bash
$ > python ./protocol/server.py
[2025-06-27 16:36:01]	[Command]	log:Command interface initialized
[2025-06-27 16:36:01]	[inMemoryDB]	log:Initialized in-memory database
[2025-06-27 16:36:01]	[Server]	log:Server started on localhost:8080
Connection from ('127.0.0.1', 50631)

$ > python ./protocol/client.py
cmd>> items
Received: [(b, 3), (c, 13), (d, 4)]
cmd>> get b
Received: 3
cmd>> exit 
Exiting...
```

## HTTP Server Example

```bash
$ > python ./protocol/httpHandler.py
[2025-06-28 12:29:12]	[Command]	log:Command interface initialized
[2025-06-28 12:29:12]	[inMemoryDB]	log:Initialized in-memory database
Starting HTTP server on port 8080...
```

## API

* `put(key, value, expiration_time=None)`: Stores a value by key. If `expiration_time` is provided, the data will expire after that many seconds. Defaults to 7 seconds.
* `get(key)`: Retrieves a value by key. Automatically deletes and returns `None` if expired.
* `delete(key)`: Deletes a key-value pair.
* `clear`: Deletes all data in the database.
* `exists(key)`: Checks if a key exists. Returns `False` if expired.
* `keys`: Returns a list of all keys (excluding expired).
* `values`: Returns a list of all values (excluding expired).
* `items`: Returns a list of all key-value pairs (excluding expired).
* `size`: Returns the number of items in the database (excluding expired).
* `begin`: Starts a transaction.
* `commit`: Commits a transaction, applying all changes.
* `rollback`: Rolls back a transaction, cancelling all changes.
* `exit`: Exits the command interface.
* `show-alias`: Prints the list of current aliases.
* `alias <alias_name> <command>`: Sets an alias for a command.

  * Example: `alias k keys` will allow `k` to run the `keys` command.
* `reset-alias`: Resets all aliases.
* `batch <commands>`: Executes multiple commands in sequence.

  * Example: `batch put a 1; put b 2; get a; get b;`.

## License

MIT License

---