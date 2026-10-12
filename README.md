# Technician Voice Assistant

Windows-first automotive assistant built for Guava AI hackathon.

## Core workflows

- Technician discovery interviews.
- Diagnostic reasoning sanity checks.
- User-provided shop-manual grounding.
- Structured JSON call reports.
- Required inbound number: `+1 240-212-2724`.

Guava provides inbound calling, speech recognition, dialog reasoning, speech generation,
structured tasks, WebRTC, and document retrieval.

## Requirements

- Windows 10 or newer.
- Python 3.11 or newer.
- `uv`.
- Guava CLI 0.47 or newer.
- Guava API key beginning with `gva-`.

## Install

```powershell
uv sync --extra dev
uv sync --project .\my-agent
```

Use `uv sync --extra dev --extra webrtc` when embedded WebRTC is required. Without
optional WebEngine package, app opens Guava WebRTC in default browser.

## Run desktop application

```powershell
uv run python .\app.py
```

Open **Guava Setup**, enter API key, then open **Voice Assistant** and select
**Start Guava**. Application securely passes key to managed child process.

## Run Guava directly

```powershell
$env:GUAVA_API_KEY = "gva-your-key"
guava run ./my-agent
```

Call `+1 240-212-2724`. Agent asks whether to start research interview or
diagnostic sanity check.

## Shop manuals

Use **Manuals** page to add authorized PDF or text files. Files remain under current
Windows user application-data directory. Restart Guava after manual changes.

## Diagnostic provider accounts

Provider passwords and Guava API key use Windows Credential Manager. Database stores
provider usernames only. MVP does not automate provider websites or bypass access controls.

## Dynamic user state

Profile page supports exactly one runtime-defined field. New calls receive field through
Guava context.

## Tests

```powershell
uv run --extra dev ruff check .
uv run --extra dev mypy src
uv run --extra dev pytest
```

## Package

```powershell
uv run pyinstaller .\technician-assistant.spec
```

Packaged application still requires Guava CLI available on `PATH`.

## Safety

Assistant provides decision support only. Verify all procedures and specifications using
approved service information. Follow high-voltage, fuel, lift, heat, rotating-equipment,
and restraint-system safety procedures.