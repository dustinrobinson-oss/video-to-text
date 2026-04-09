"""
transcribe_recordings.py
========================
RealWork Labs — Shared Transcription Automation

Scans an input folder for audio/video files, transcribes each using
OpenAI Whisper, saves .txt transcripts, and archives the originals.

Any team member can run this on their machine. No GPU required.

Setup (one time):
    pip install openai-whisper
    # Also needs ffmpeg installed:
    #   macOS:   brew install ffmpeg
    #   Windows: choco install ffmpeg  (or download from ffmpeg.org)
    #   Linux:   sudo apt install ffmpeg

Usage:
    python transcribe_recordings.py
    python transcribe_recordings.py --input /path/to/recordings --output /path/to/transcripts
    python transcribe_recordings.py --model small  (for better accuracy, slower)

Defaults:
    Input:   ~/Documents/Claude/sources/recordings/
    Output:  ~/Documents/Claude/sources/transcripts/
    Archive: ~/Documents/Claude/sources/recordings/Archive/
    Model:   base
"""

import argparse
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

AUDIO_VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm",
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac",
}

DEFAULT_INPUT = Path.home() / "Documents" / "Claude" / "sources" / "recordings"
DEFAULT_OUTPUT = Path.home() / "Documents" / "Claude" / "sources" / "transcripts"


def parse_args():
    parser = argparse.ArgumentParser(description="Transcribe audio/video files using Whisper.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                        help="Folder containing audio/video files to transcribe")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Folder to save .txt transcripts")
    parser.add_argument("--model", default="base",
                        choices=["tiny", "tiny.en", "base", "base.en", "small",
                                 "small.en", "medium", "medium.en", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--language", default="en",
                        help="Language code (default: en)")
    parser.add_argument("--keep-originals", action="store_true",
                        help="Don't move originals to Archive after transcribing")
    return parser.parse_args()


def find_media_files(input_dir: Path) -> list[Path]:
    """Find all audio/video files in input_dir (not subdirectories)."""
    return sorted([
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_VIDEO_EXTENSIONS
    ])


def safe_output_path(output_dir: Path, stem: str, suffix: str = ".txt") -> Path:
    """Return a unique output path, appending date if file already exists."""
    candidate = output_dir / f"{stem}{suffix}"
    if not candidate.exists():
        return candidate
    dated = output_dir / f"{stem}_{datetime.now().strftime('%Y-%m-%d')}{suffix}"
    if not dated.exists():
        return dated
    # Last resort: add timestamp
    return output_dir / f"{stem}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}{suffix}"


def safe_archive_path(archive_dir: Path, filename: str) -> Path:
    """Return a unique archive path."""
    candidate = archive_dir / filename
    if not candidate.exists():
        return candidate
    stem = Path(filename).stem
    ext = Path(filename).suffix
    return archive_dir / f"{stem}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}{ext}"


def main():
    args = parse_args()

    # Validate input folder
    if not args.input.is_dir():
        print(f"Error: Input folder not found: {args.input}")
        print(f"Create it with: mkdir -p \"{args.input}\"")
        sys.exit(1)

    # Create output and archive folders
    args.output.mkdir(parents=True, exist_ok=True)
    archive_dir = args.input / "Archive"
    archive_dir.mkdir(exist_ok=True)

    # Find files
    media_files = find_media_files(args.input)
    if not media_files:
        print(f"No new recordings found in {args.input}")
        sys.exit(0)

    print(f"Found {len(media_files)} file(s) to transcribe:")
    for f in media_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f.name} ({size_mb:.1f} MB)")

    # Load Whisper
    try:
        import whisper
    except ImportError:
        print("\nError: openai-whisper not installed.")
        print("Run: pip install openai-whisper")
        sys.exit(1)

    print(f"\nLoading Whisper '{args.model}' model...")
    model = whisper.load_model(args.model)
    print("Model loaded.\n")

    # Process each file
    total_start = time.time()
    results = {"success": [], "failed": []}

    for i, filepath in enumerate(media_files, 1):
        print(f"[{i}/{len(media_files)}] Transcribing: {filepath.name} ...", flush=True)
        start = time.time()

        try:
            result = model.transcribe(str(filepath), fp16=False, language=args.language)
            txt_path = safe_output_path(args.output, filepath.stem)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(result["text"])

            elapsed = time.time() - start
            print(f"  Saved: {txt_path.name} ({elapsed:.1f}s)")
            results["success"].append((filepath.name, txt_path.name))

            # Archive original
            if not args.keep_originals:
                dest = safe_archive_path(archive_dir, filepath.name)
                shutil.move(str(filepath), str(dest))
                print(f"  Archived: {dest.name}")

        except Exception as e:
            elapsed = time.time() - start
            print(f"  FAILED ({elapsed:.1f}s): {e}")
            results["failed"].append((filepath.name, str(e)))

    # Summary
    total = time.time() - total_start
    print(f"\n{'='*50}")
    print(f"Done in {total:.1f}s")
    print(f"  Transcribed: {len(results['success'])}")
    print(f"  Failed:      {len(results['failed'])}")

    if results["failed"]:
        print("\nFailed files:")
        for name, err in results["failed"]:
            print(f"  - {name}: {err}")

    print(f"\nTranscripts saved to: {args.output}")
    if not args.keep_originals:
        print(f"Originals archived to: {archive_dir}")


if __name__ == "__main__":
    main()
