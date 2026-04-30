# HCP CRM AI — Log Interaction Screen

> AI-first CRM module for Healthcare-Professional (HCP) interactions. A field rep types a natural-language note into the AI assistant; a **LangGraph** agent extracts CRM fields and fills the form. Form fields stay writable, but the spec's intent is that you drive the form through chat instead of typing.


##  Demo Overview

This project is an AI-first CRM system where healthcare sales reps can log interactions using natural language instead of filling forms manually.

### 🔹 Example

User input:
"Met Dr. Smith today, discussed Product X, sentiment positive."

AI automatically:
- Extracts doctor name, date, topic, sentiment
- Fills the form
- Validates required fields
- Saves to database

### 💡 Key Idea
Instead of manually entering data, users interact with the system like a conversation.


## Features

- Split-screen UI: editable form on the left, AI assistant chat on the right
- Natural-language **logging** — describe the interaction once, the form fills itself
- Natural-language **editing** — say "Sorry, the name was actually Dr. John"; only that field changes
- **Validation** of required fields before the row is persisted
- Automatic **sentiment** classification and one-line **summary**
- Every successful interaction is saved to **Postgres** and listable via `GET /interactions`

## Stack

| Layer    | Tech                                                        |
| -------- | ----------------------------------------------------------- |
| Frontend | React 19, **Redux Toolkit**, Google **Inter** font          |
| Backend  | **FastAPI** (Python 3.12, also works on 3.11)               |
| Agent    | **LangGraph** (5 tools)                                     |
| LLM      | Groq — `llama-3.3-70b-versatile` (spec's `gemma2-9b-it` was decommissioned by Groq; this is one of the spec's listed alternatives) |
| DB       | PostgreSQL                                                  |

## The 5 LangGraph tools

| # | Tool                  | Purpose                                                                 |
|---|-----------------------|-------------------------------------------------------------------------|
| 1 | `log_interaction`     | LLM extracts `hcp_name`, `date`, `interaction_type`, `attendees`, `topics`, `sentiment`, `materials_shared`. Today's date is injected into the prompt so "today" / "yesterday" resolve correctly. |
| 2 | `edit_interaction`    | Re-extracts from a correction message and overwrites **only** the fields the user mentioned, preserving the rest. |
| 3 | `validate_interaction`| Checks required fields (`hcp_name`, `date`, `interaction_type`, `topics`) and returns `{ is_valid, missing_fields }`. |
| 4 | `sentiment_tool`      | Classifies sentiment as positive / neutral / negative.                  |
| 5 | `summary_tool`        | Generates a one-line natural-language summary.                          |

Graph flow: `log → (edit if correction) → validate → sentiment → summary → END`.
If `validation.is_valid`, the row is persisted to Postgres and `saved_id` is returned.

## Endpoints

- `POST /chat` — body `{ message, current? }`. Runs the graph and returns the merged form state, validation, summary, and `saved_id` (if persisted).
- `GET /interactions?limit=50` — returns the most recent saved interactions.

Open `http://localhost:8000/docs` while the backend runs for an interactive Swagger UI.

## Project layout

```
frontend/
  src/
    App.js              split-screen UI (form + AI chat)
    App.css             matches the provided mockup
    store/
      index.js          Redux store
      formSlice.js      form state + applyAiUpdate (merges only non-null fields)
      chatSlice.js      chat history + sendMessage thunk
backend/
  main.py               FastAPI app, /chat and /interactions
  agent.py              LangGraph wiring
  tools.py              5 tools + Groq client
  db.py                 Postgres helpers (init_db, save_interaction, list_interactions)
  state.py              InteractionState TypedDict
  requirements.txt
.env.example            template for required environment variables
INSTRUCTIONS.txt        full step-by-step setup guide
```

## Run locally — step by step (Windows)

> macOS / Linux users: replace `py -3.12` with `python3.12` and `venv\Scripts\Activate.ps1` with `source venv/bin/activate`. Everything else is the same.

### Step 1 — Install the prerequisites (one-time)

1. **Python 3.12** — https://www.python.org/downloads/release/python-3120/
   During install, tick **"Add Python to PATH"**.
2. **Node.js 20+ (LTS)** — https://nodejs.org/
3. **PostgreSQL 16** — https://www.postgresql.org/download/windows/
   Remember the password you set for the `postgres` user.
4. **Groq API key** (free) — https://console.groq.com/keys

Verify in PowerShell:
```powershell
python --version       # should show 3.12.x
node --version         # should show v20.x or higher
psql --version         # should show PostgreSQL 16.x
```

### Step 2 — Unzip and open the project

1. Right-click `hcp-crm-package.zip` → **Extract All…** → pick a folder (e.g. `C:\Projects\hcp-crm`).
2. Open that folder in **VS Code** (`File > Open Folder`).

### Step 3 — Create the database (one-time)

In PowerShell:
```powershell
psql -U postgres
```
Enter your postgres password, then:
```sql
CREATE DATABASE hcp_crm;
\q
```

### Step 4 — Set up and start the backend

Open a terminal in VS Code (**Ctrl + `**) and run:

```powershell
cd backend
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> If PowerShell blocks the activation script, run this once and reopen the terminal:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

Set the two environment variables (only for this terminal session):
```powershell
$env:GROQ_API_KEY = "paste_your_groq_key_here"
$env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/hcp_crm"
```

Start the backend:
```powershell
python main.py
```

You should see `Uvicorn running on http://0.0.0.0:8000`. Leave this terminal running.

✅ Test it: open http://localhost:8000/docs in your browser — you'll see the FastAPI Swagger UI.

### Step 5 — Set up and start the frontend

Open a **second** terminal in VS Code (click the **+** in the terminal panel):

```powershell
cd frontend
npm install
npm start
```

> The `npm install` will print a long list of `npm warn deprecated …` and a "28 vulnerabilities" notice. These are normal for Create-React-App in 2026 and don't affect anything. **Do NOT run `npm audit fix --force`** — it will break the build.

After 30–60 seconds your browser will auto-open at **http://localhost:3000**.

### Step 6 — Try it out

In the chat panel on the right, type:

> Met Dr. Smith today, discussed Product X efficacy. Sentiment was positive and I shared brochures.

The form on the left fills in. Then send a correction:

> Sorry, the name was actually Dr. John and the sentiment was negative.

Only the name and sentiment change — the rest is preserved.

To see saved rows: open http://localhost:8000/interactions

### Common problems

| Problem | Fix |
|---|---|
| `python` shows the wrong version | Use `py -3.12` instead of `python` |
| `Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once |
| Backend logs `connection refused` to Postgres | Postgres service isn't running — open Services app, start `postgresql-x64-16`. Also double-check your password in `DATABASE_URL`. |
| Chat shows `ECONNREFUSED` | Backend isn't running — check the Step 4 terminal |
| Groq returns `model_decommissioned` | Open `backend/tools.py` and switch the model name to a current one from https://console.groq.com/docs/models |

## Sample chat messages to test

**Log an interaction**
> Met Dr. Smith today, discussed Product X efficacy. Sentiment was positive and I shared the brochures.

**Edit it**
> Sorry, the name was actually Dr. John and the sentiment was negative.

**Log with partial info (will report missing fields)**
> Had a quick call about pricing.

**Log via call type**
> Called Dr. Patel yesterday about the new launch, neutral sentiment, no materials shared.

After saving, hit `GET http://localhost:8000/interactions` to see the rows.

## Notes for reviewers

- The form remains user-writable on purpose. The spec says "do not fill the form manually" — meaning the rep should drive it via chat — but does not require the inputs to be disabled. Keeping them writable preserves accessibility and lets the rep make small corrections without re-prompting the AI.
- The original spec referenced Groq's `gemma2-9b-it`. Groq has since decommissioned that model (the API returns `model_decommissioned`). I switched to `llama-3.3-70b-versatile`, which the spec explicitly lists as an acceptable alternative.
- The interactions table is created automatically the first time the backend starts (`init_db()` in `backend/db.py`).

## Python 3.12 compatibility — what was updated

The project originally targeted Python 3.11. To make it work cleanly on Python 3.12 (and stay forward-compatible up to 3.13), the following changes were made:

| Change | Where | Why |
|---|---|---|
| `requires-python` widened to `>=3.11,<3.14` | `pyproject.toml` | Officially declares support for Python 3.11, 3.12 and 3.13. |
| Postgres driver is **`psycopg` v3** (not `psycopg2`) | `backend/requirements.txt` | `psycopg2` has historically lagged on new Python releases and needs C build tools on Windows. `psycopg[binary]>=3.3.3` ships pre-built wheels for Python 3.12 — installs cleanly with no compiler. |
| `pydantic >= 2.13.3` | `backend/requirements.txt` | Pydantic v2 is fully supported on Python 3.12. The older Pydantic v1 line (used by some older FastAPI tutorials) does not work well on 3.12. |
| `fastapi >= 0.136.1` and `uvicorn[standard] >= 0.46.0` | `backend/requirements.txt` | These versions explicitly support Python 3.12. Older FastAPI / Starlette versions had asyncio behavior that broke on 3.12. |
| `langgraph >= 1.1.10` and `langchain-groq >= 1.1.2` | `backend/requirements.txt` | First versions of these libraries that test cleanly against Python 3.12. |
| Setup commands use `py -3.12` / `python3.12` | `README.md`, `INSTRUCTIONS.txt` | Picks the right interpreter even on machines with multiple Python versions installed. |
| `from typing import Optional` kept (instead of `X | None`) | `backend/main.py` | `X | None` syntax works on 3.12, but `Optional` keeps the code readable for anyone still on 3.11. |

##  Implementation Note

During development, I rebuilt the project to ensure full compatibility with Python 3.12 and newer environments.

This allowed me to:
- Use updated dependencies (FastAPI, Pydantic v2, psycopg v3)
- Avoid compatibility issues with older libraries
- Ensure the project runs cleanly on modern setups

No functional changes were made — only improvements in stability and environment support.

**No code changes were needed** beyond dependencies and docs — Python 3.12 is fully compatible with the syntax used. If you want to upgrade further to **Python 3.13**, the same `requirements.txt` works; just install Python 3.13 and use `py -3.13` in the setup commands.
