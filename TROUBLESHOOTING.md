# User Troubleshooting Guide

This guide covers Windows 10 and newer.

## Quick recovery checklist

Try these steps first:

1. Close the application.
2. Confirm internet access.
3. Confirm `guava --version` works.
4. Start the application with `run.cmd`.
5. Save the Guava API key again.
6. Restart the Guava worker.
7. Wait for `ready` status.

Never share API keys.
Never paste keys into logs.

## Application does not open

### `run.cmd` shows missing uv

Install the `uv` package manager.
Then reopen PowerShell.

Verify installation:

```powershell
uv --version
```

If PowerShell still cannot find it:

```powershell
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
uv --version
```

Then double-click `run.cmd` again.

### Launcher closes immediately

Run it from PowerShell.
This preserves error output:

```powershell
.\run.cmd
```

If environment setup fails:

```powershell
uv sync --extra dev
```

Resolve the first reported error.
Then retry `run.cmd`.

### Manual Python launch fails

Recreate installed dependencies:

```powershell
uv sync --extra dev
uv run python .\app.py
```

Confirm Python 3.11 or newer:

```powershell
python --version
```

### Packaged executable fails

Use the current source launcher first:

```powershell
.\run.cmd
```

If source works, rebuild executable:

```powershell
uv run pyinstaller .\technician-assistant.spec
```

New executable appears under `dist`.

## Guava worker problems

### Status says `Add a Guava API key`

Open **Guava Setup**.
Enter a valid `gva-...` key.
Select **Save Guava settings**.

The field clears after saving.
This behavior protects the key.

### API key is rejected

Confirm these requirements:

- Value starts with `gva-`.
- Value contains no surrounding spaces.
- Value has not expired.
- Correct Guava organization issued it.

Remove the saved key.
Then save the correct key.

### Status stays `starting`

Check the worker log panel.
Then verify Guava CLI:

```powershell
guava --version
```

If command is unavailable:

- Install Guava CLI.
- Reopen the application.
- Ensure Guava exists on `PATH`.

Expected local location may resemble:

```text
%LOCALAPPDATA%\guava\bin\guava.exe
```

Restart the application after changes.

### Status changes to `error`

Read the final worker log lines.
Common causes include:

- Invalid Guava API key.
- Missing Guava CLI.
- Network access failure.
- Invalid agent configuration.
- Dependency installation failure.

Run the worker directly for details:

```powershell
$env:GUAVA_API_KEY = "gva-your-key"
guava run .\my-agent
```

Close that worker before retrying.
Do not run duplicate workers.

### Worker stops unexpectedly

Confirm no second worker exists.
Then select **Restart** once.

If failure repeats:

```powershell
uv sync --project .\my-agent
guava run .\my-agent
```

Record the first actual error.
Ignore later cascading errors.

## Phone call problems

### Inbound call does not connect

Confirm worker status shows `ready`.
Then call:

```text
+1 240-212-2724
```

Also confirm:

- Worker remains running.
- Internet connection remains active.
- Guava project remains enabled.
- Caller can reach United States numbers.

### Call connects without profile state

Open **Profile**.
Complete all three controls:

- Field label.
- Field type.
- Field value.

Select **Save runtime field**.
Confirm `Runtime field saved.`

The field enters new calls only.
Start another call after saving.

### Profile value is rejected

Use valid values:

- Text: any non-empty text.
- Number: valid numeric text.
- Boolean: `true` or `false`.

Only one runtime field exists.
Saving another replaces it.

## WebRTC problems

### WebRTC code is rejected

Generate a fresh code:

```powershell
guava widget
```

Code must start with `grtc-`.
Save it under **Guava Setup**.

### WebRTC opens externally

Embedded WebRTC is optional.
Default browser opens when unavailable.

Install embedded browser support:

```powershell
uv sync --extra dev --extra webrtc
```

Restart the application afterward.

### Microphone does not work

Check Windows permissions:

1. Open **Settings**.
2. Open **Privacy**.
3. Open **Microphone**.
4. Enable microphone access.
5. Enable desktop application access.

For external WebRTC, also check browser permissions.
Close other applications holding microphone.

## Manual and retrieval problems

### Manual does not appear

Supported formats are:

- `.pdf`
- `.txt`

Use **Manuals** to import files.
Do not copy unsupported formats.

### Manual appears but is ignored

Select **Restart** under **Voice Assistant**.
Manual indexing occurs during worker startup.

For PDFs, confirm text is selectable.
Image-only scans may contain no extractable text.
Convert scans with OCR first.

### Manual answer lacks evidence

Possible causes include:

- Relevant manual is missing.
- PDF has no text layer.
- Question uses different terminology.
- Required specification is absent.

Ask a narrower question.
Include vehicle and component details.
Always verify approved service information.

### Manual cannot be removed

Stop the Guava worker.
Close applications using that file.
Then retry **Remove selected**.

## Reports and saved data

### New report does not appear

Complete the active call workflow.
Reports save after workflow completion.
Then select **Refresh**.

Interrupted calls may lack reports.

### Stored settings seem missing

Application data is user-specific.
Use the same Windows account.

Default data location:

```text
%LOCALAPPDATA%\GuavaHackathon\TechnicianVoiceAssistant
```

Important contents include:

- `assistant.db`
- `manuals\`

API keys are not stored there.
Windows Credential Manager stores secrets.

### Reset local application data

Close the application first.
Back up needed reports and manuals.

Rename this directory:

```text
%LOCALAPPDATA%\GuavaHackathon\TechnicianVoiceAssistant
```

Restarting creates clean data.
Saved reports and profile state reset.

Remove credentials separately:

1. Open **Credential Manager**.
2. Open **Windows Credentials**.
3. Locate `TechnicianVoiceAssistant`.
4. Remove only intended entries.

## Provider account problems

### Provider account does not save

All fields are required:

- Provider.
- Username.
- Password.

Windows Credential Manager must be available.
Passwords never enter SQLite.

### Provider portal does not sign in

Portal login remains manual.
The application does not automate websites.
Open the official portal.
Then enter credentials manually.

## Repair commands

Run project checks:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src
```

Rebuild root environment:

```powershell
Remove-Item -Recurse -Force .\.venv
uv sync --extra dev
```

Rebuild agent environment:

```powershell
Remove-Item -Recurse -Force .\my-agent\.venv
uv sync --project .\my-agent
```

Only remove environments while stopped.
These commands preserve user data.

## Information for support

Collect these details:

- Windows version.
- Application launch method.
- `python --version` output.
- `uv --version` output.
- `guava --version` output.
- Worker status.
- First relevant error line.
- Whether phone or WebRTC failed.
- Whether source launcher works.

Exclude these details:

- Guava API keys.
- Provider passwords.
- Customer personal information.
- Full private call transcripts.
