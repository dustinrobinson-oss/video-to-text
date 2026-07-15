# Transcription Tool: Complete Playbook for Claude

This playbook enables any Claude instance (Cowork, Claude Code, or Claude Desktop) to set up, configure, and run the RealWork Labs transcription tool from scratch. Follow every step in order. Do not skip steps. Do not improvise. Do not ask the user for information you can discover by running commands.

---

## CONTEXT

**What this tool does:** Transcribes audio and video files to text using OpenAI Whisper. Runs 100% locally. No API key. No data leaves the machine.

**Repository:** https://github.com/dustinrobinson-oss/video-to-text

**Owner:** Dustin Robinson (dustin.robinson@realworklabs.com), Finance and Accounting Manager at RealWork Labs.

**Primary use case:** Transcribe CS call recordings, sales calls, training recordings, and meeting audio for analysis.

---

## PHASE 1: ENVIRONMENT DISCOVERY

Before installing anything, discover the machine's current state. Run all of these and read the output before proceeding.

```powershell
# Check Python
python --version

# Check Git
git --version

# Check ffmpeg
ffmpeg -version 2>$null | Select-Object -First 1

# Check pip packages
pip show openai-whisper 2>$null | Select-String "Version"
pip show yt-dlp 2>$null | Select-String "Version"
pip show openpyxl 2>$null | Select-String "Version"

# Check if repo already exists
ls "$HOME\Documents\video-to-text\transcribe_recordings.py" 2>$null
ls "$HOME\Documents\Claude\work\automations\transcription-tool\transcribe_recordings.py" 2>$null

# Check folder structure
ls "$HOME\Documents\Claude\sources\recordings" 2>$null
ls "$HOME\Documents\Claude\sources\transcripts" 2>$null

# Check if OneDrive paths exist (may or may not be the correct paths)
ls "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources" 2>$null

# Check Google Drive for Desktop
ls "G:\My Drive" 2>$null

# Get Windows username
$env:USERNAME
```

**Decision tree after discovery:**

- Python missing: STOP. Tell user to install Python 3.10+ from python.org.
- Git missing: STOP. Tell user to install Git from git-scm.com.
- ffmpeg missing: Install in Phase 2.
- pip packages missing: Install in Phase 2.
- Repo already cloned: Skip clone in Phase 2. Use the path where it already exists.
- Folders already exist: Skip folder creation in Phase 3.

**CRITICAL: Path detection.** Use `$HOME` or `$env:USERPROFILE` in PowerShell to resolve the current user's home directory. Never hardcode a username. Example working paths:

- Script location: `$HOME\Documents\Claude\work\automations\transcription-tool\`
- Recordings: `$HOME\Documents\Claude\sources\recordings`
- Transcripts: `$HOME\Documents\Claude\sources\transcripts`

These may or may not be under OneDrive. Verify which paths exist before running any commands. Never assume OneDrive. Use whatever paths the discovery step confirms.

---

## PHASE 2: INSTALL DEPENDENCIES

Only install what is missing based on Phase 1 results.

### ffmpeg (requires Admin PowerShell)

If ffmpeg is not installed, tell the user:

> "I need to install ffmpeg. This requires an Administrator PowerShell window. Please open PowerShell as Administrator, run `choco install ffmpeg -y`, then close the admin window and tell me when it is done."

If Chocolatey is not installed either, tell the user to run this in Admin PowerShell first:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Then `choco install ffmpeg -y`.

Claude cannot run Admin PowerShell commands directly. The user must do this step.

### Python packages

```powershell
pip install openai-whisper yt-dlp openpyxl
```

This installs:
- openai-whisper: local speech-to-text (downloads model weights on first use, ~1.5GB for medium)
- yt-dlp: downloads audio from YouTube, Zoom, Vimeo, and hundreds of other sites
- openpyxl: reads Excel files (.xlsx)

### Clone the repository (if not already present)

```powershell
cd "$HOME\Documents"
git clone https://github.com/dustinrobinson-oss/video-to-text.git
```

If the repo already exists at a different path (like `Documents\Claude\work\automations\transcription-tool\`), use that path for all subsequent commands. Do NOT clone a second copy.

**Verify the script exists:**
```powershell
python PATH_TO_SCRIPT\transcribe_recordings.py --help
```

Replace PATH_TO_SCRIPT with the actual path. You should see full help text with all flags listed.

---

## PHASE 3: CREATE FOLDER STRUCTURE

Only create folders that do not already exist.

```powershell
mkdir "$HOME\Documents\Claude\sources\recordings" -Force
mkdir "$HOME\Documents\Claude\sources\transcripts" -Force
mkdir "$HOME\Documents\Claude\sources\recordings\Archive" -Force
```

If the user's paths are under OneDrive instead, use those paths:
```powershell
mkdir "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\recordings" -Force
mkdir "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts" -Force
```

**Always confirm which paths are correct before creating folders.** Run `ls` on both options from Phase 1 and use whichever one exists or the user confirms.

---

## PHASE 4: SET PATH VARIABLES

For the rest of this playbook, define these variables based on what you discovered. Set them in PowerShell at the start of every session:

```powershell
$SCRIPT_DIR = "$HOME\Documents\Claude\work\automations\transcription-tool"
$RECORDINGS = "$HOME\Documents\Claude\sources\recordings"
$TRANSCRIPTS = "$HOME\Documents\Claude\sources\transcripts"
```

Adjust these to match the actual paths on the machine. Every command below uses these variables.

---

## PHASE 5: RUNNING TRANSCRIPTIONS

### Mode 1: Local audio/video files

Drop .mp4, .mp3, .wav, .mov, .avi, .mkv, .webm, .m4a, .flac, .ogg, or .aac files into the recordings folder, then:

```powershell
cd $SCRIPT_DIR
python transcribe_recordings.py --input $RECORDINGS --output $TRANSCRIPTS --model medium
```

The script will:
1. Scan the input folder for media files
2. Check the output folder for existing transcripts (dedup by filename stem)
3. Transcribe only new files
4. Save .txt transcripts to the output folder
5. Move originals to recordings/Archive/
6. Never delete anything

### Mode 2: YouTube or web URLs

Single URL:
```powershell
cd $SCRIPT_DIR
python transcribe_recordings.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output $TRANSCRIPTS --model medium
```

Multiple URLs:
```powershell
python transcribe_recordings.py --url "https://url1" --url "https://url2" --output $TRANSCRIPTS --model medium
```

### Mode 3: Batch URLs via links.txt

Create a file called `links.txt` in the recordings folder with one URL per line. Lines starting with # are ignored.

```powershell
python transcribe_recordings.py --input $RECORDINGS --output $TRANSCRIPTS --model medium
```

The script auto-detects links.txt, downloads audio, transcribes, and archives the file.

### Mode 4: Excel file with recording URLs

```powershell
python transcribe_recordings.py --xlsx "C:\path\to\file.xlsx" --output $TRANSCRIPTS --model medium
```

Default URL column: "Recording Link". To change:
```powershell
python transcribe_recordings.py --xlsx file.xlsx --url-column "All Recording Links (chronological)" --output $TRANSCRIPTS
```

Default filename columns: Account, Touchplan. To change:
```powershell
python transcribe_recordings.py --xlsx file.xlsx --name-columns "Account" "Owner" --output $TRANSCRIPTS
```

### Mode 5: Google Drive for Desktop (local sync)

If Google Drive for Desktop is installed and files are in the user's own Drive (not shared folders from other people):

```powershell
# Find audio files on Drive
Get-ChildItem "G:\My Drive" -Recurse -Include *.mp4,*.m4a,*.mp3,*.wav | Select-Object FullName,Length

# Run against the folder
python transcribe_recordings.py --input "G:\My Drive\FOLDER_NAME" --output $TRANSCRIPTS --model medium
```

**WARNING: Shared folders from other people (folders owned by someone else that were shared with the user) do NOT reliably sync to the local Drive mount.** If the folder was shared by someone else:

1. Open Google Drive in the browser
2. Go to the shared folder
3. Select all files
4. Download (comes as a zip)
5. Extract to the recordings folder
6. Run Mode 1 against the local recordings folder

Do not waste time trying to make shared folder shortcuts work with Drive for Desktop. It is a known limitation.

---

## PHASE 6: MODEL SELECTION

| Model  | Speed (per 1hr audio, CPU) | Accuracy | Use for                    |
|--------|----------------------------|----------|----------------------------|
| tiny   | ~10 min                    | Low      | Quick tests, validation    |
| base   | ~20 min                    | Fair     | Fast drafts                |
| small  | ~60 min                    | Good     | Speed-sensitive runs       |
| medium | ~3 hours                   | High     | Scheduled/unattended runs  |
| large  | ~6 hours                   | Highest  | Critical accuracy needs    |

Default is `medium`. Use `--model tiny` for testing. The first run with any model downloads the weights (tiny ~75MB, medium ~1.5GB). This is a one-time download.

---

## PHASE 7: TASK SCHEDULER (AUTOMATED RUNS)

For scheduled unattended transcription, set up Windows Task Scheduler.

Tell the user to:

1. Open Task Scheduler (search "Task Scheduler" in Start menu)
2. Click "Create Basic Task"
3. Name: `TranscribeRecordings`
4. Trigger: Weekly, select Monday/Wednesday/Friday, 9:00 AM
5. Action: Start a program
6. Program/script: `python`
7. Arguments (single line, replace USERNAME with the actual Windows username from `$env:USERNAME`):

```
"C:\Users\USERNAME\Documents\Claude\work\automations\transcription-tool\transcribe_recordings.py" --input "C:\Users\USERNAME\Documents\Claude\sources\recordings" --output "C:\Users\USERNAME\Documents\Claude\sources\transcripts" --model medium
```

Task Scheduler does not expand `$HOME`. You must use the full literal path with the actual username. Run `$env:USERNAME` in PowerShell to get it.

8. Check "Open the Properties dialog" before finishing
9. In Properties, under General: check "Run whether user is logged on or not"
10. Click OK. Enter Windows password when prompted.

Claude cannot create scheduled tasks directly. The user must do this step.

---

## PHASE 8: VERIFICATION

After setup is complete, run this verification sequence:

```powershell
# 1. Confirm script runs
cd $SCRIPT_DIR
python transcribe_recordings.py --help

# 2. Confirm folders exist
ls $RECORDINGS
ls $TRANSCRIPTS

# 3. Confirm a test transcription works (use tiny model for speed)
# Option A: if there are files in the recordings folder
python transcribe_recordings.py --input $RECORDINGS --output $TRANSCRIPTS --model tiny

# Option B: if no local files, use a short YouTube video
python transcribe_recordings.py --url "https://www.youtube.com/watch?v=jNQXAC9IVRw" --output $TRANSCRIPTS --model tiny

# 4. Confirm transcript was created
ls $TRANSCRIPTS\*.txt
```

If step 4 shows a .txt file, the tool is fully operational.

---

## TROUBLESHOOTING

**"openai-whisper not installed"**: `pip install openai-whisper`

**"yt-dlp not installed"**: `pip install yt-dlp`

**"openpyxl not installed"**: `pip install openpyxl`

**"ffmpeg not found"**: User must run `choco install ffmpeg -y` in Admin PowerShell, then restart PowerShell.

**FP16 warning on CPU**: Normal. The script handles this automatically by setting fp16=False. No action needed.

**"No new files to transcribe"**: All files in the input folder already have matching transcripts in the output folder. Check the output folder. To re-transcribe, delete or move the existing .txt file first.

**"Could not copy Chrome cookie database"**: Chrome locks its cookie database while running. Close Chrome first, or use `--cookies-from-browser edge` instead. Only applies to URL-based downloads.

**Google Drive URL returns 403 Forbidden**: The file is private. Do NOT use `--url` with Google Drive links. Download files from Drive manually (browser) and use Mode 1 (local files). Or use Drive for Desktop if the files are in the user's own Drive.

**Google Drive shared folder not syncing locally**: Shared folders owned by other users do not reliably sync via Drive for Desktop shortcuts. Download files manually through the browser.

**Excel column not found**: Column names are case-sensitive and may include trailing spaces. Run `--help` and verify the exact column name from the Excel file.

**Transcription very slow**: Expected on CPU. A 30-minute recording takes ~1.5 hours with medium model. Switch to `--model base` for faster results at lower accuracy.

**Script path confusion**: The script may exist at `Documents\video-to-text\` (if freshly cloned) or at `Documents\Claude\work\automations\transcription-tool\` (Dustin's working copy). Always run Phase 1 discovery to find the actual location. Never guess.

---

## QUICK REFERENCE COMMANDS

```powershell
# Navigate to script
cd "$HOME\Documents\Claude\work\automations\transcription-tool"

# Transcribe local files (production)
python transcribe_recordings.py --input "$HOME\Documents\Claude\sources\recordings" --output "$HOME\Documents\Claude\sources\transcripts" --model medium

# Transcribe local files (quick test)
python transcribe_recordings.py --input "$HOME\Documents\Claude\sources\recordings" --output "$HOME\Documents\Claude\sources\transcripts" --model tiny

# Transcribe a YouTube URL
python transcribe_recordings.py --url "URL_HERE" --output "$HOME\Documents\Claude\sources\transcripts" --model medium

# Transcribe Excel file of URLs
python transcribe_recordings.py --xlsx "PATH_TO_XLSX" --output "$HOME\Documents\Claude\sources\transcripts" --model medium

# Check what files exist
ls "$HOME\Documents\Claude\sources\recordings"
ls "$HOME\Documents\Claude\sources\transcripts"

# Find audio files on Google Drive (if Drive for Desktop installed)
Get-ChildItem "G:\My Drive" -Recurse -Include *.mp4,*.m4a,*.mp3,*.wav | Select-Object FullName,Length
```

---

## WHAT CLAUDE SHOULD DO WHEN ASKED TO TRANSCRIBE

When the user says "transcribe these files" or "run the transcription tool" or similar:

1. Run Phase 1 discovery (if not already done this session)
2. Confirm the script path, recordings path, and transcripts path
3. Check what files are in the recordings folder
4. Run the appropriate mode based on what the user provided (local files, URLs, Excel)
5. Use `--model medium` unless the user specifies otherwise or asks for a quick test
6. After completion, report: number of files transcribed, output location, any failures
7. Offer to read/analyze the transcripts if relevant

When the user provides audio files (uploads, shared Drive links, or drops files in a folder):

1. Move or copy the files to the recordings folder if they are not already there
2. Run the transcription command
3. Report results

Do NOT ask the user to run commands manually if Claude has Bash/shell access. Run them directly.

---

*Last updated: 2026-07-15*
