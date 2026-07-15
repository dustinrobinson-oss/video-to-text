# Transcription Tool: Complete Setup Playbook

This document contains every step needed to set up the RealWork Labs transcription tool from scratch on a Windows machine. Follow each section in order. Do not skip steps. Do not improvise.

## Prerequisites

- Windows 10/11 with PowerShell
- Python 3.10+ installed (check: `python --version`)
- Git installed (check: `git --version`)
- Internet connection
- Chocolatey installed (check: `choco --version`). If not installed: open Admin PowerShell and run `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`

## Step 1: Install ffmpeg

Open PowerShell as Administrator (right-click, Run as administrator):

```powershell
choco install ffmpeg -y
```

Close the admin window. Open a regular PowerShell for all remaining steps.

## Step 2: Install Python packages

```powershell
pip install openai-whisper yt-dlp openpyxl
```

This installs three packages:
- openai-whisper: local speech-to-text engine (no API key needed)
- yt-dlp: downloads audio from YouTube, Zoom, and hundreds of other sites
- openpyxl: reads Excel files (.xlsx)

## Step 3: Clone the repository

```powershell
cd "$HOME\Documents"
git clone https://github.com/dustinrobinson-oss/video-to-text.git
```

Verify:
```powershell
ls "$HOME\Documents\video-to-text\transcribe_recordings.py"
```

You should see the file listed. If not, the clone failed.

## Step 4: Create source folders

```powershell
mkdir "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\recordings" -Force
mkdir "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts" -Force
```

If the user does NOT use OneDrive, use these paths instead:
```powershell
mkdir "$HOME\Documents\Claude\sources\recordings" -Force
mkdir "$HOME\Documents\Claude\sources\transcripts" -Force
```

## Step 5: Verify the installation

Run a quick syntax check:
```powershell
cd "$HOME\Documents\video-to-text"
python transcribe_recordings.py --help
```

You should see the full help text with all options listed. If you get an import error, go back to Step 2.

## Step 6: Test with a YouTube URL (quick validation)

Pick any short public YouTube video (under 2 minutes) and run:

```powershell
cd "$HOME\Documents\video-to-text"
python transcribe_recordings.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts" --model tiny
```

Use `--model tiny` for the test (fastest). The default model is `medium` for production runs.

If this produces a .txt file in the transcripts folder, the tool is working.

## Step 7: Set up Windows Task Scheduler (optional, for automated runs)

This makes the script run automatically on a schedule.

1. Open Task Scheduler (search "Task Scheduler" in Start menu)
2. Click "Create Basic Task"
3. Name: `TranscribeRecordings`
4. Trigger: Weekly, select Monday/Wednesday/Friday, 9:00 AM
5. Action: Start a program
6. Program/script: `python`
7. Arguments:

For OneDrive users:
```
"C:\Users\YOUR_USERNAME\Documents\video-to-text\transcribe_recordings.py" --input "C:\Users\YOUR_USERNAME\OneDrive - RealWork Labs\Documents\Claude\sources\recordings" --output "C:\Users\YOUR_USERNAME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts" --model medium
```

For non-OneDrive users:
```
"C:\Users\YOUR_USERNAME\Documents\video-to-text\transcribe_recordings.py" --input "C:\Users\YOUR_USERNAME\Documents\Claude\sources\recordings" --output "C:\Users\YOUR_USERNAME\Documents\Claude\sources\transcripts" --model medium
```

Replace YOUR_USERNAME with the actual Windows username.

8. Check "Open the Properties dialog" before finishing
9. In Properties, under General: check "Run whether user is logged on or not"
10. Click OK. Enter your Windows password when prompted.

## Usage Reference

### Transcribe local files

Drop audio/video files (.mp4, .mp3, .wav, .mov, .avi, .mkv, .webm, .m4a, .flac, .ogg, .aac) into the recordings folder, then:

```powershell
cd "$HOME\Documents\video-to-text"
python transcribe_recordings.py --input "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\recordings" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts"
```

### Transcribe a URL

```powershell
cd "$HOME\Documents\video-to-text"
python transcribe_recordings.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts"
```

Multiple URLs:
```powershell
python transcribe_recordings.py --url "https://url1" --url "https://url2" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts"
```

### Transcribe an Excel file of URLs

```powershell
cd "$HOME\Documents\video-to-text"
python transcribe_recordings.py --xlsx "C:\path\to\file.xlsx" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts"
```

The script reads the "Recording Link" column by default. That is the correct column for most use cases. To use a different column:
```powershell
python transcribe_recordings.py --xlsx file.xlsx --url-column "Some Other Column"
```

To change the transcript filename (built from Excel columns):
```powershell
python transcribe_recordings.py --xlsx file.xlsx --name-columns "Account" "Touchplan" "Owner "
```

### Zoom Contact Center recordings

Zoom CCI links (zoom.us/cci/...) require authentication. The script auto-detects these and pulls cookies from Chrome. You must be logged into Zoom in your browser before running the command. To use a different browser:

```powershell
python transcribe_recordings.py --xlsx file.xlsx --cookies-from-browser edge
```

### Batch via links.txt

Create a file called `links.txt` in the recordings folder with one URL per line:
```
https://www.youtube.com/watch?v=abc123
https://vimeo.com/456789
# Lines starting with # are ignored
```

The script picks them up on the next run, downloads, transcribes, and archives the links.txt.

## How it works

1. Reads URLs from all sources (--url flags, links.txt, --xlsx)
2. Downloads audio via yt-dlp (extracts audio track, saves as .mp3)
3. Scans recordings folder for local audio/video files
4. Dedup: checks existing transcripts, skips already-processed files
5. Transcribes with OpenAI Whisper (runs 100% locally, no API key, no data leaves the machine)
6. Saves .txt transcripts to the output folder
7. Archives originals to recordings/Archive/
8. Nothing is ever deleted

## Model reference

| Model  | Speed (per 1hr audio, CPU) | Accuracy |
|--------|----------------------------|----------|
| tiny   | ~10 min                    | Low      |
| base   | ~20 min                    | Fair     |
| small  | ~60 min                    | Good     |
| medium | ~3 hours                   | High     |
| large  | ~6 hours                   | Highest  |

Default: medium. Use `--model tiny` or `--model base` for quick tests. Use `--model medium` or `--model large` when accuracy matters and time does not.

## Troubleshooting

**"openai-whisper not installed"**: Run `pip install openai-whisper`

**"yt-dlp not installed"**: Run `pip install yt-dlp`

**"openpyxl not installed"**: Run `pip install openpyxl`

**"ffmpeg not found"**: Run `choco install ffmpeg -y` in Admin PowerShell, then restart PowerShell

**FP16 warning**: Normal on CPU. The script already handles this by setting fp16=False.

**Zoom download fails**: Make sure you are logged into Zoom in Chrome (or whichever browser you specified with --cookies-from-browser). Your Zoom account must have permission to access the recordings.

**Excel column not found**: Run with `--help` and check the exact column name. Column names are case-sensitive and include trailing spaces if the Excel has them.

**Transcription takes a long time**: Expected on CPU with medium/large models. A 30-minute recording takes ~1.5 hours with medium on CPU. Switch to `--model base` for faster results at lower accuracy.
