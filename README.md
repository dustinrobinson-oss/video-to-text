# Transcription Tool

Automated audio/video transcription for RealWork Labs. Drop recordings into a folder, run the script, get text transcripts. No GPU required.

## Setup

**Prerequisites:**
- Python 3.9+
- ffmpeg

**Install ffmpeg:**
```bash
# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
# or download from https://ffmpeg.org/download.html

# Linux
sudo apt install ffmpeg
```

**Install Whisper:**
```bash
pip install openai-whisper
```

## Usage

**Basic (uses default folders):**
```bash
python transcribe_recordings.py
```

Default folders (created automatically if they don't exist):
- Input: `~/Documents/Claude/sources/recordings/`
- Output: `~/Documents/Claude/sources/transcripts/`
- Archive: `~/Documents/Claude/sources/recordings/Archive/`

**Custom folders:**
```bash
python transcribe_recordings.py --input /path/to/recordings --output /path/to/transcripts
```

**Options:**
```
--input       Folder containing audio/video files (default: ~/Documents/Claude/sources/recordings/)
--output      Folder to save .txt transcripts (default: ~/Documents/Claude/sources/transcripts/)
--model       Whisper model size: tiny, base, small, medium, large (default: base)
--language    Language code (default: en)
--keep-originals  Don't move originals to Archive after transcribing
```

**Better accuracy (slower):**
```bash
python transcribe_recordings.py --model small
```

## How It Works

1. Scans the input folder for audio/video files (.mp4, .mov, .mp3, .wav, .m4a, etc.)
2. Transcribes each file using OpenAI Whisper (runs locally, no API key needed)
3. Saves each transcript as a .txt file in the output folder
4. Moves processed originals to the Archive subfolder so they aren't re-transcribed

Existing files are never overwritten. If a transcript name conflicts, a date suffix is appended.

## Supported File Types

**Video:** .mp4, .mov, .avi, .mkv, .webm
**Audio:** .mp3, .wav, .m4a, .flac, .ogg, .aac
