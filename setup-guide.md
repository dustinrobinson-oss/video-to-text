# Transcription Tool Setup

Run these commands in PowerShell in order. No steps to skip, no decisions to make.

## 1. Install ffmpeg (Admin PowerShell required)

Right-click PowerShell, select "Run as administrator", then:

```powershell
choco install ffmpeg -y
```

Close the admin window when done. Open a regular PowerShell for everything below.

## 2. Install Python packages

```powershell
pip install openai-whisper yt-dlp
```

## 3. Clone the repo

```powershell
cd "$HOME\Documents"
git clone https://github.com/dustinrobinson-oss/video-to-text.git
```

## 4. Create folders

```powershell
mkdir "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\recordings" -Force
mkdir "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts" -Force
```

## 5. Test with a local file

Drop any .mp4, .mp3, or .wav file into the recordings folder above, then:

```powershell
cd "$HOME\Documents\video-to-text"
python transcribe_recordings.py --input "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\recordings" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts" --model base
```

Use `--model base` for a quick test. Scheduled runs default to `medium` for better accuracy.

## 6. Test with a YouTube URL

```powershell
cd "$HOME\Documents\video-to-text"
python transcribe_recordings.py --url "https://www.youtube.com/watch?v=VIDEO_ID_HERE" --output "$HOME\OneDrive - RealWork Labs\Documents\Claude\sources\transcripts" --model base
```

Replace VIDEO_ID_HERE with an actual video ID.

## Done

Transcripts land in the transcripts folder as .txt files. Originals get archived automatically. Nothing is deleted.

Full usage details are in the repo README.
