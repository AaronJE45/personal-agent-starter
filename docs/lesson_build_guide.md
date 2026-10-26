# Lesson build guide

The course website supplies the explanations and MCQs. This repository supplies
the project exercises and module reference code. There is no repository-based
progress check. Never change a module number to unlock functionality: build the
code incrementally, or copy a reference snapshot using the recovery instructions.

## Module 1 — Lessons 1–5

1. Read the example conversation in README.md. Identify the assistant's purpose.
2. Trace user → model → tool → result. Nothing calls a real model yet.
3. Create your own repository from the Metana template; clone it.
4. Follow setup_guides.md and run `python main.py`. Expected: local starter reply.
5. Edit `AGENT_NAME`, restart, and personalise the README. Commit your changes.

## Module 2 — Lessons 6–10

Open `solutions/module_2/agent.py` as a reference. Work in the root `agent.py`.
The `requests` library and JSON HTTP protocol keep model calls visible without
requiring a framework. Tool definitions in the reference helper are supplied for
Module 4; `with_tools=False` excludes them from Module 2 requests.

6. Add `request_model`: validate configuration, create the JSON body, call the
   generateContent endpoint, extract the first candidate's content.
7. Edit `SYSTEM_INSTRUCTION` in `config.py`; include it in `systemInstruction`.
8. Build a user content object: `{"role": "user", "parts": [{"text": message}]}`.
9. Call the helper from `Agent.chat`, returning its visible text. Inspect the
   supplied terminal loop and use `/exit`. Each request is independent for now.
10. Configure `.env` and add the reference's readable HTTP/connection errors.
    Run a conversation, then temporarily remove the model ID to see the missing
    configuration message. Restore it afterwards.

Expected: actual model replies; no tools or previous-message memory yet.

## Module 3 — Lessons 11–15

Work in root `tools.py`. Use `solutions/module_3/tools.py` for comparison. Its
SQLite branches are pre-supplied infrastructure but remain disabled until Module 5.

11. Inspect the five tool signatures. Each tool returns a Python dictionary/list.
12. Build per-user task lists and implement `add_task` and `list_tasks`.
13. Implement `complete_task` by ID; report false when no matching task exists.
14. Build per-user note lists and implement `save_note` and substring search.
15. Reject blank/oversized text and invalid task IDs. Return copies of stored data.

Manual practice from the project root:

```sh
python -c "from tools import add_task, list_tasks; print(add_task('Practise Python')); print(list_tasks())"
```

Expected: task ID 1 and a list containing that task in the **same process**.
In-memory data is lost when the command exits. Model-driven tools arrive next.

## Module 4 — Lessons 16–20

Compare `solutions/module_4/agent.py` with your root `agent.py`.

16. Define JSON schemas for the five tools. Tool inputs do not include `user_id`.
17. Add model content to the conversation and inspect its `functionCall` parts.
18. Dispatch only names in `TOOL_FUNCTIONS`; supply `user_id` from the application.
    Reject model arguments that attempt to supply their own `user_id`.
19. Append matching `functionResponse` objects and ask the model again. Preserve
    the original model content (including IDs and thought signatures) unchanged.
20. Wrap requests in `range(config.MAX_STEPS)` and return a helpful stop message
    at the limit. Errors become tool results, not a program crash.

Expected: “Add practise Python to my tasks” executes a real tool. Ask “List tasks”
next. There is no cross-message chat history yet, but in-memory tools retain data
while the process runs. Some actions may succeed even if a later model call fails.

## Module 5 — Lessons 21–25

Compare the full Module 5 snapshot. `storage.py` is already supplied.

21. Store complete turns in `self.history`, keyed by user ID.
22. Keep chat history separate from notes/tasks; it is temporary context.
23. Enable `USE_DATABASE = True` and connect tools to `storage.db_*` helpers.
24. Pass the same application-controlled user ID through every storage operation.
25. Bound history by complete turns, not individual messages (a tool call and its
    result must stay together). `/reset` removes only that user's chat history.

Expected: save a task, exit, restart, list tasks: the task remains. Prior chat
history does not survive a restart. Terminal data and WhatsApp data are separate.
Use `solutions/module_5` if you need to restore the complete implementation.

## Module 6 — Lessons 26–30

26. Read `whatsapp_server.py`: verification GET, signed event POST, background job,
    tool/agent processing, outbound reply. Transport code is pre-built.
27. Complete the official test-number/recipient setup in setup_guides.md.
28. Start the server and tunnel; verify `/webhook` and subscribe to messages.
29. In `handle_message`, replace the starter return with exactly:

```python
return assistant.chat(text, user_id=sender)
```

30. Restart the server. Send a greeting, add a task, list tasks, save/search a note.
    Expected: replies arrive in your personal WhatsApp conversation.

## Module 7 — Lessons 31–35

31. Follow the manual finish checklist in setup_guides.md.
32. Read troubleshooting.md and practise stopping/restarting your app and tunnel.
33. Personalise instructions. Keep tool names/schemas and user isolation intact.
34. Replace the README's “My assistant” section with your own description and
    fictional example messages. Commit source code; exclude private local data.
35. Explain the message → model → tool → result → reply flow in your own words.

Reference Module 7 keeps the completed Module 6 code. You provide the project
identity and README content. Answer each lesson's MCQ on the site to record
progress; this repository neither verifies completion nor issues certificates.
