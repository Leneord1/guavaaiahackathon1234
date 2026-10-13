# Technician Voice Assistant

Windows-first automotive voice assistant.
Built for Guava AI hackathon.

## Team

**Team:** Sunny Side Up  
**Team member:** Sankalp Amaravadi

The application supports two workflows.
First, it interviews automotive technicians.
Second, it reviews diagnostic reasoning.
Guava AI powers every conversation.

## Problem

Automotive diagnosis often becomes fragmented.
Technicians switch between scan tools.
They search multiple information systems.
They also consult experienced technicians.
This process consumes valuable time.

TorqueCheck provides a spoken review.
It gathers relevant vehicle evidence.
It checks diagnostic reasoning.
It highlights missing confirmation tests.
It also flags safety concerns.

The assistant does not authorize repairs.
Technicians retain final decision authority.

## Guava AI Integration

Guava remains the core technology.
It provides these capabilities:

- Inbound telephone call handling.
- Real-time speech recognition.
- Conversational reasoning and routing.
- Natural text-to-speech output.
- Structured task field collection.
- WebRTC voice conversations.
- Manual-grounded `DocumentQA` retrieval.

Required inbound number:

```text
+1 240-212-2724
```

The Python expert connects through:

```powershell
guava run ./my-agent
```

## Core workflows

### Research interview

The assistant introduces research intent.
It avoids product sales language.
It asks ten discovery questions.
Questions cover these areas:

- Recent difficult diagnoses.
- First information source used.
- Time needed for confidence.
- Master technician consultation goals.
- Comebacks and incorrect parts.
- Trust concerns with online content.
- Under-hood lookup habits.
- Voice assistant usefulness.
- Tool purchasing responsibility.
- Desired shop improvements.

Answers become structured report fields.
Original detail remains available.

### Diagnostic sanity check

The assistant gathers case facts.
It requests these diagnostic details:

- Vehicle and configuration.
- Customer complaint and conditions.
- Trouble codes and scan data.
- Tests and measured results.
- Current diagnostic hypothesis.

It then reviews reasoning.
Review covers these checks:

- Conflicting observations.
- Missing confirmation tests.
- Disconfirming evidence.
- Relevant safety precautions.
- Highest-information next test.
- Current confidence level.

The assistant separates manual facts.
General reasoning stays clearly identified.
Unsupported specifications are never invented.

## Windows Application

PySide6 provides the desktop interface.
The application contains seven pages:

### Home

Shows product purpose.
Displays required phone number.
Shows safety limitations.

### Guava Setup

Accepts a Guava API key.
Input remains visually masked.
Windows Credential Manager protects it.
Optional WebRTC codes are supported.

### Voice Assistant

Starts the Guava worker.
Shows current worker status.
Displays redacted process logs.
Supports stopping and restarting.
Prevents duplicate local workers.

### Reports

Lists completed call reports.
Shows results as raw JSON.
Includes source manual filenames.

### Manuals

Imports authorized PDF documents.
Text documents also work.
Files remain outside source control.
Restarting Guava refreshes indexing.

### Provider Accounts

Stores diagnostic software accounts.
Supported systems include:

- ALLDATA.
- Identifix.
- Mitchell 1 ProDemand.
- Ford Motorcraft Service.
- GM ACDelco TDS.
- Stellantis wiTECH.
- Toyota TIS.
- Honda TechInfo.
- Nissan TechInfo.
- Hyundai and Kia service.
- BMW AOS.
- Mercedes-Benz XENTRY.
- Volkswagen and Audi erWin.
- Custom provider entries.

Passwords use Windows Credential Manager.
Only usernames reach SQLite.
Official portals open manually.
Website automation is intentionally disabled.

### Profile

Defines one dynamic user field.
Supported types include:

- Text.
- Number.
- Boolean.

The current field reaches Guava.
`call.add_info` injects its value.

## Architecture

Desktop application manages setup.
It starts Guava through `QProcess`.
The child command remains unchanged:

```powershell
guava run ./my-agent
```

The Guava agent handles calls.
It routes the selected workflow.
`DocumentQA` searches supplied manuals.
SQLite stores completed structured reports.
Windows Credential Manager stores secrets.

Core services remain UI-independent.
A mobile client can follow later.

## Project Structure

```text
.
├── app.py
├── my-agent/
│   ├── main.py
│   ├── guava.toml
│   └── pyproject.toml
├── src/technician_assistant/
│   ├── agent.py
│   ├── interview.py
│   ├── diagnostic.py
│   ├── knowledge.py
│   ├── credentials.py
│   ├── process_manager.py
│   ├── profile.py
│   ├── providers.py
│   ├── storage.py
│   └── ui/
├── tests/
├── pyproject.toml
└── technician-assistant.spec
```

## Requirements

- Windows 10 or newer.
- Python 3.11 or newer.
- `uv` package manager.
- Guava CLI 0.47 or newer.
- Guava API key beginning with `gva-`.

Check Guava installation:

```powershell
guava --version
```

## Installation

Install desktop dependencies:

```powershell
uv sync --extra dev
```

Install Guava agent dependencies:

```powershell
uv sync --project .\my-agent
```

Install embedded WebRTC support:

```powershell
uv sync --extra dev --extra webrtc
```

Without WebEngine, WebRTC opens externally.
Default browser handles microphone access.

### Troubleshooting `uv`

See [User Troubleshooting Guide](TROUBLESHOOTING.md) for complete recovery steps.

If PowerShell cannot find `uv` after installation,
refresh the current terminal's `PATH`:

```powershell
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
uv --version
```

Restarting PowerShell also refreshes `PATH`.

## Running Desktop Application

Double-click:

```text
run.cmd
```

The launcher creates the environment when needed.

Alternatively, run from PowerShell:

```powershell
uv run python .\app.py
```

Then complete these steps:

1. Open **Guava Setup**.
2. Enter Guava API key.
3. Save Guava settings.
4. Open **Voice Assistant**.
5. Select **Start Guava**.
6. Wait for `ready` status.
7. Call required phone number.

The API key stays protected.
It enters only child environment.
Logs automatically redact key values.

## Run Guava directly

Set API key:

```powershell
$env:GUAVA_API_KEY = "gva-your-key"
```

Start inbound agent:

```powershell
guava run ./my-agent
```

Then call:

```text
+1 240-212-2724
```

The agent discloses AI usage.
It requests desired operating mode.

## WebRTC

Create a WebRTC code:

```powershell
guava widget
```

Enter returned `grtc-...` code.
Use the Guava Setup page.
The worker serves both channels.

## Shop manuals

Only import authorized documents.
Supported formats are PDF and text.

Add manuals through the desktop interface:

1. Start the desktop application.
2. Select **Manuals** in the sidebar.
3. Select **Add PDF or text manual**.
4. Choose one or more `.pdf` or `.txt` files.
5. Select **Open** to import them.
6. Confirm filenames appear in the manual list.
7. Open **Voice Assistant**.
8. Select **Restart** to rebuild the Guava index.

To delete a manual, select its filename.
Then select **Remove selected**.
Restart Guava after every manual change.

The application extracts document text.
Each filename becomes stable source.
Guava indexes extracted manual content.
Answers request source filename citations.

Missing evidence triggers explicit fallback.
General reasoning remains clearly labeled.

## Data Storage

Application data uses user-local storage.
Stored data includes:

- Structured call reports.
- Manual source filenames.
- Dynamic profile field.
- Provider usernames.

Stored data excludes:

- Guava API keys.
- Provider passwords.
- Guava audio recordings.
- Guava call transcripts.

Guava retains its own conversations.
Review them through Guava dashboard.

## Security

Secrets use Windows Credential Manager.
No secrets enter repository files.
No secrets enter SQLite.
No secrets enter displayed logs.

Provider accounts remain vault-only.
No website controls are bypassed.
No unofficial scraping is performed.

## Development

Run desktop application:

```powershell
uv run python .\app.py
```

Run agent independently:

```powershell
guava run ./my-agent
```

Application data paths use `platformdirs`.
Generated databases remain ignored.

## Tests

```powershell
uv run --extra dev ruff check .
uv run --extra dev mypy src
uv run --extra dev pytest
```

Current verification covers:

- Interview workflow routing.
- Diagnostic workflow staging.
- Manual source indexing.
- Missing-manual fallback.
- Report persistence.
- Dynamic profile validation.
- Guava key protection.
- Provider password protection.
- Process environment injection.
- Process log redaction.
- PySide6 application startup.

## Package

```powershell
uv run pyinstaller .\technician-assistant.spec
```

Executable output appears under `dist/`.
Guava CLI must remain available.
Its executable must be on `PATH`.

## Hackathon Demo Flow

Recommended demonstration sequence:

1. Start Windows application.
2. Show protected Guava setup.
3. Import one sample manual.
4. Start managed Guava worker.
5. Confirm `ready` worker status.
6. Call `+1 240-212-2724`.
7. Select diagnostic sanity check.
8. Describe a diagnostic case.
9. Review manual-grounded response.
10. Open saved JSON report.
11. Repeat using interview mode.

## Safety

Assistant provides decision support only.
Verify all procedures independently.
Use approved service information.
Follow manufacturer safety procedures.

Critical risks include:

- High-voltage systems.
- Fuel system pressure.
- Vehicle lifting.
- Rotating equipment.
- Hot components.
- Supplemental restraint systems.

Stop when evidence is missing.
Escalate unsafe diagnostic steps.