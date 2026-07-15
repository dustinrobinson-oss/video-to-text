# Video-to-Text

Automated audio/video transcription for RealWork Labs. Handles local files, YouTube links, and Excel spreadsheets full of Zoom recording URLs. No GPU required.

## Quick Start

**1. Clone the repo:**
```
git clone https://github.com/dustinrobinson-oss/video-to-text.git
```

**2. Install dependencies (one time):**
```
pip install openai-whisper yt-dlp openpyxl
```

ffmpeg is also required:
- Windows (Admin PowerShell): `choco install ffmpeg -y`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

**3. Create your folders:**
```powershell
mkdir "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\recordings" -Force
mkdir "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts" -Force
```

## Usage

### Transcribe local files

Drop audio/video files into the recordings folder, then:
```powershell
cd "$HOME\Documents\video-to-text"
python transcribe_recordings.py --input "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\recordings" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts"
```

### Transcribe a YouTube URL

```powershell
python transcribe_recordings.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts"
```

### Transcribe an Excel file of Zoom recording links

```powershell
python transcribe_recordings.py --xlsx "C:\path\to\calls.xlsx" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts"
```

This reads the "Recording Link" column by default. For multi-recording rows, use the "All Recording Links" column:
```powershell
python transcribe_recordings.py --xlsx calls.xlsx --url-column "All Recording Links (chronological)" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts"
```

Zoom Contact Center links require authentication. The script auto-detects these and pulls cookies from Chrome. You must be logged into Zoom in your browser. To specify a different browser:
```powershell
python transcribe_recordings.py --xlsx calls.xlsx --cookies-from-browser edge --output ...
```

### Batch URLs via links.txt

Create a `links.txt` file in your recordings folder with one URL per line. The script picks them up on the next run.

## What It Does

1. Reads URLs from --url flags, links.txt, and/or --xlsx Excel files
2. Downloads audio via yt-dlp (supports YouTube, Zoom, Vimeo, hundreds more)
3. Scans the input folder for local audio/video files
4. Dedup check: skips files that already have transcripts
5. Transcribes using OpenAI Whisper (runs locally, no API key needed)
6. Saves .txt transcripts with metadata headers (from Excel rows)
7. Archives processed files automatically

No files are ever deleted. No duplicates are ever created.

## Options

```
--input              Folder with local audio/video files
--output             Folder for .txt transcripts
--url                URL to transcribe (repeatable)
--xlsx               Excel file containing URLs to transcribe
--url-column         Column name with URLs (default: Recording Link)
--name-columns       Columns to build filename from (default: Account Touchplan)
--cookies-from-browser  Browser for authenticated downloads (chrome, firefox, edge)
--model              Whisper model: tiny, base, small, medium (default), large
--language           Language code (default: en)
--keep-originals     Don't move originals to Archive
```

## Model Selection

| Model  | Speed (per 1hr audio, CPU) | Accuracy | Best for                |
|--------|----------------------------|----------|-------------------------|
| tiny   | ~10 min                    | Low      | Quick tests             |
| base   | ~20 min                    | Fair     | Fast drafts             |
| small  | ~60 min                    | Good     | Speed-sensitive runs    |
| medium | ~3 hours                   | High     | Scheduled/unattended    |
| large  | ~6 hours                   | Highest  | Critical accuracy needs |

Default is `medium` for best accuracy on unattended scheduled runs.

## Supported File Types

Video: .mp4, .mov, .avi, .mkv, .webm
Audio: .mp3, .wav, .m4a, .flac, .ogg, .aac
