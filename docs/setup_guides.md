# Setup guides

Start with a computer (not only a phone), internet, a text editor, and WhatsApp.
Use fake notes and tasks. Allow installation time beyond coding time if needed.

## 1. Get the project

Install [Git](https://git-scm.com/downloads) or [GitHub Desktop](https://desktop.github.com/).
On the published template, choose **Use this template → Create a new repository**.
Choose your own account as owner and `metana-personal-agent` as the name.
Clone that repository using **Code → HTTPS**, or GitHub Desktop. In a terminal,
replace YOUR-USERNAME with your GitHub username:

```sh
git clone https://github.com/YOUR-USERNAME/metana-personal-agent.git
cd metana-personal-agent
```

For the unpublished instructor copy, open the `personal-agent-starter` folder
instead. All commands below run from the folder containing `main.py`.
Do not create your environment inside a solution snapshot.

## 2. Windows PowerShell

Install Python 3.13 from [python.org](https://www.python.org/downloads/).
Enable the installer option to add Python to PATH if offered, then reopen PowerShell.

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe main.py
```

Calling the environment's Python directly avoids activation policy errors.
Do not rerun `Copy-Item` if `.env` already contains your configuration.

## 3. macOS

Install Python 3.13 from [python.org](https://www.python.org/downloads/).
If HTTPS reports a certificate error, run the supplied **Install Certificates.command**
in the installed Python application folder. Then open a fresh Terminal:

```sh
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

## 4. Linux

Use your distribution's Python 3.11+ packages. On Ubuntu/Debian:

```sh
sudo apt update
sudo apt install python3 python3-venv python3-pip git
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

If your distribution provides an older Python, use its documented supported
upgrade process rather than replacing the system Python. Never use `sudo pip`.

## 5. Expected first conversation

```text
Metana Buddy is ready. Type /exit to leave or /reset to clear chat history.
You: hello
Metana Buddy: Starter running! In Module 2 you will connect an AI model.
You: /exit
Goodbye!
```

Edit `AGENT_NAME` in `config.py`, restart, and see the name change.

## 6. Module 2: configure a model

1. Open [Google AI Studio](https://aistudio.google.com/).
2. Confirm your age, account, and region are eligible. Remain on the free tier;
   do not link billing to finish this course.
3. Create an API key. Open the local `.env` file in your editor and paste it as
   `GEMINI_API_KEY=...` (do not paste it into a terminal command or commit).
4. Choose a currently available free-tier text model supporting function calling.
   Set its exact API model ID as `GEMINI_MODEL=...`; do not include `models/`.
5. Implement Module 2 using the [build guide](lesson_build_guide.md), or recover
   using the Module 2 reference. Restart the program after changes to `.env`.

Do not share your `.env`. A model request is real internet traffic. Free quotas
are limited: avoid repeatedly sending the same request when an error occurs.

## 7. Module 6: configure WhatsApp

Start with the [official developer hub](https://whatsappbusiness.com/developers/developer-hub/)
and [Meta get-started flow](https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started).
Dashboard labels and eligibility can change. Use the official test number, not a
purchased number. If asked to buy service or enable billing, stop and check that
you are in the testing flow. No bypass is provided for provider account restrictions.

1. Sign in to Meta for Developers; create an app with the WhatsApp use case.
2. Open WhatsApp's API setup and use the supplied test number.
3. Add your own recipient phone and finish its verification.
4. Copy the **Phone Number ID** (not the phone number itself), temporary access token,
   supported Graph API version, and the app's **App Secret** into `.env`.
5. Set `WHATSAPP_ALLOWED_SENDER` to your recipient's international number, country
   code and digits only (no `+`, spaces or punctuation). Only that phone is accepted.
6. Choose a long random `WHATSAPP_VERIFY_TOKEN` and enter the same value later in Meta.
   This is your own verification string; it is different from the access token
   and the App Secret. You can generate one with:

```sh
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

7. Start the server in terminal A (Windows: use `.\.venv\Scripts\python.exe`):

```sh
python whatsapp_server.py
```

8. Install `cloudflared` following [Cloudflare's OS-specific downloads](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/).
   Example package-manager commands if you already use them:

| OS | Command |
| --- | --- |
| Windows | `winget install --id Cloudflare.cloudflared` |
| macOS with Homebrew | `brew install cloudflared` |
| Linux | Follow the official package instructions for your distribution |

9. In terminal B, start a temporary tunnel (no account/domain needed):

```sh
cloudflared tunnel --url http://127.0.0.1:8000
```

10. Copy the HTTPS `https://...trycloudflare.com` URL. In Meta's webhook configuration,
    enter **that URL plus `/webhook`**, and your chosen verify token. Verify and save.
11. Subscribe the app to WhatsApp **messages** events using the official setup flow.
    Ensure the app is connected/subscribed to the test WhatsApp Business Account
    where the setup flow requests it. Delivery-status events alone are not messages.
12. Send a message **from your own WhatsApp** to the Meta test number. The supplied
    starter replies “Webhook connected! ...”. In Lesson 29 replace the marked return
    in `handle_message` with `return assistant.chat(text, user_id=sender)`.
13. Restart the server and send “Add practise Python to my tasks”, then “List my tasks”.

Keep both terminals and your computer awake. A restarted quick tunnel usually has
a new URL: update and verify Meta's callback again. The app binds to localhost;
the tunnel is the temporary public entry point. Stop both processes with Ctrl+C.
Never enable Flask debug mode on this exposed server.

## Manual finish checklist

- Terminal and WhatsApp both answer.
- Adding, listing and completing a task works.
- Searching a saved note returns the note.
- Saved data survives a restart from Module 5 onward.
- `/reset` clears chat context but leaves saved tasks and notes.
- `.env`, phone numbers, databases, and chat screenshots are not in Git.
- Your README describes what you learned.

These are self-checks, not grading. Course progress is recorded by MCQs on the site.
