# Reference snapshots and recovery

Each `module_1` … `module_7` folder contains all six runtime Python files plus
requirements and configuration templates. These are complete end-of-module
snapshots. Module 7 intentionally keeps Module 6 functionality: it adds manual
checks, documentation and personalisation rather than another technical feature.

| Snapshot | Behaviour |
| --- | --- |
| Module 1 | Local starter reply; no key or tool calls |
| Module 2 | Single model request per message; no tools or conversation memory |
| Module 3 | Same chat plus tools callable directly in Python; in-memory data |
| Module 4 | Tool-calling loop and bounded steps; no cross-message history |
| Module 5 | Bounded per-user history and persistent SQLite notes/tasks |
| Module 6 | Agent connected to the verified WhatsApp transport |
| Module 7 | Same complete app, ready to document and share |

## Restore safely

Save a commit or a copy of your edited Python files first. Stop the server before
recovery. From the **project root**, replace `module_3` below with the desired
module. Run just one of these OS-specific commands.

macOS/Linux:

```sh
cp solutions/module_3/main.py solutions/module_3/config.py solutions/module_3/agent.py solutions/module_3/tools.py solutions/module_3/storage.py solutions/module_3/whatsapp_server.py .
```

Windows PowerShell:

```powershell
Copy-Item solutions/module_3/main.py, solutions/module_3/config.py, solutions/module_3/agent.py, solutions/module_3/tools.py, solutions/module_3/storage.py, solutions/module_3/whatsapp_server.py -Destination .
```

Keep your existing root `.env` and `data/`. Copying the Python files does not erase
them. Reapply your chosen name/instructions in `config.py`, then restart the app.
Do not run inside `solutions/module_N`: each snapshot loads only its own `.env`,
so it deliberately will not discover the root's secrets or database.

Reference code is for independent recovery and comparison; the site records MCQ
completion, not code correctness. Read the relevant lesson before copying code.
