# Build Your Personal AI Agent — by Metana

A free, self-paced, approximately 20-hour project for Python beginners. Create
one personal assistant, keep your work in your own GitHub repository, and chat
with it through WhatsApp while your computer is running.

**Start here:** [Setup](docs/setup_guides.md) → [Lesson build guide](docs/lesson_build_guide.md)
→ [Troubleshooting](docs/troubleshooting.md).

## Your first run

Use Python 3.11 or newer (3.13 recommended). Open a terminal in this folder.

macOS / Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe main.py
```

Expected: `Metana Buddy is ready.` Send a message to see a local starter reply.
No API key is needed for Module 1. `/exit` leaves; the real `/reset` command is
implemented in Module 5. The first reply is deliberately not an AI response.

## Own your project

Once Metana publishes this folder as `metana-learning/personal-agent-starter`,
choose **Use this template → Create a new repository**. Suggested name:
`metana-personal-agent`. Clone **your** repository and open its folder.
Until published, an instructor can distribute this directory as a standalone ZIP.
No remote repository is created by these files.

After each module, save your work:

```sh
git add main.py config.py agent.py tools.py storage.py whatsapp_server.py README.md
git commit -m "Complete Module 1"
git push
```

If Git asks who you are, configure your name and a GitHub-provided no-reply email
using GitHub's [commit identity guide](https://docs.github.com/en/get-started/getting-started-with-git/setting-your-commit-email-address).
Use GitHub Desktop if you prefer a graphical commit/push flow. GitHub authentication
uses its browser/credential-manager flow or a token, not your account password.
Never paste authentication tokens into code or screenshots.

## What's in the project?

| File | Role |
| --- | --- |
| `main.py` | Terminal input, `/exit`, and readable errors |
| `config.py` | Name, instructions, explicit local `.env` loading |
| `agent.py` | Starts with a local reply; build model calls, tools, loop, history |
| `tools.py` | Five exercise functions for notes and tasks |
| `storage.py` | Supplied SQLite helpers, connected in Module 5 |
| `whatsapp_server.py` | Supplied verified webhook and Lesson 29 connection hook |
| `solutions/module_1/` … `module_7/` | Complete end-of-module runtime snapshots |
| `docs/` | Setup, build steps, recovery, limits, sidebar blueprint |

## Learning milestones

1. Run and personalise your starter (2h).
2. Chat with a model from the terminal (2.5h).
3. Build notes and task tools (3h).
4. Connect an explicit tool-calling agent loop (3h).
5. Keep conversation context and persist data (2.5h).
6. Connect your own phone to the official WhatsApp test environment (4h).
7. Check, document, and share your project (3h).

The course site records progress through end-of-lesson MCQs only. This repository
has no student grading, GitHub Actions, or personalised support. Commits save work;
they do not complete lessons. [Support sidebar](docs/support_sidebar.md).

## Free learning, practical limits

You need a computer, internet, GitHub account, eligible model account, and access to
the Meta developer testing flow plus a WhatsApp phone. No paid hosting is required.
The free-tier model must support function calling. Choose a current eligible model
in AI Studio and set `GEMINI_MODEL`; we deliberately do not hardcode a model that
might be retired or paid-only. See [limits and token refresh](docs/free_tier_limits.md).
Account eligibility and provider quotas can block the live demo; no free provider
access is guaranteed. Keep billing disabled. This is a temporary local learning
setup, not a promise of permanent free hosting.

Use fictional data. `.env`, `data/`, SQLite files, and virtual environments must not
be committed. An API request sends your message to the selected provider.

## My assistant

- Name: Metana Buddy
- Purpose: My personal notes-and-tasks assistant
- Example: “Add practise Python to my tasks.”
- What I learned: _Add your own explanation after Module 7._

Built through Metana's **Build Your Personal AI Agent** course.
Technical progression inspired by *Build an AI Agent from Scratch* by Jungjun Hur
(Manning). These are simplified, original course exercises, not the full book
implementation. See [LICENSE](LICENSE).
# personal-agent-starter
