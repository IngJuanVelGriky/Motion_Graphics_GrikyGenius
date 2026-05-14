#!/usr/bin/env python3
"""
generate_layout.py — Pipeline to auto-generate motion graphics JSON from video.

Steps:
  1. Extract audio from MP4 using ffmpeg
  2. Transcribe with Groq Whisper API
  3. Generate editorial highlights with Groq LLM
  4. Assemble final VideoLayout JSON
  5. Auto-register composition in Root.tsx

Usage:
  # Single video
  python generate_layout.py --video ../public/"Mi Video.mp4"

  # Batch: process all MP4s in a folder
  python generate_layout.py --batch ../public/

  # Options
  python generate_layout.py --video ../public/video.mp4 --force-transcribe --no-register
"""

import argparse
import glob
import httpx
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# ─── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
TRANSCRIPTS_DIR = PROJECT_DIR / "transcripts"
DATA_DIR = PROJECT_DIR / "src" / "data"
ROOT_TSX_PATH = PROJECT_DIR / "src" / "Root.tsx"
PROMPT_TEMPLATE_PATH = SCRIPT_DIR / "prompt_template.txt"
EXAMPLE_JSON_PATH = DATA_DIR / "t1-modelado-relacional.json"

# ─── Icon list (must match src/lib/icons.ts) ─────────────────────────────────

# Categorized icon catalog — helps the LLM pick semantically appropriate icons.
# All 287 Feather icons from react-icons/fi are available.
ICON_CATEGORIES = {
    "data & analytics": [
        "FiDatabase", "FiBarChart", "FiBarChart2", "FiPieChart", "FiTrendingUp",
        "FiTrendingDown", "FiActivity", "FiPercent", "FiHash", "FiTable",
    ],
    "technology & code": [
        "FiCode", "FiTerminal", "FiCpu", "FiServer", "FiHardDrive", "FiCloud",
        "FiCloudOff", "FiCloudLightning", "FiWifi", "FiWifiOff", "FiBluetooth",
        "FiMonitor", "FiSmartphone", "FiTablet", "FiTv", "FiAirplay",
        "FiGitBranch", "FiGitCommit", "FiGitMerge", "FiGitPullRequest",
        "FiCodesandbox", "FiCodepen", "FiCommand",
    ],
    "communication": [
        "FiMail", "FiInbox", "FiSend", "FiMessageCircle", "FiMessageSquare",
        "FiPhone", "FiPhoneCall", "FiPhoneIncoming", "FiPhoneOutgoing",
        "FiMic", "FiMicOff", "FiVideo", "FiVideoOff", "FiVoicemail",
        "FiRadio", "FiRss", "FiAtSign",
    ],
    "media & content": [
        "FiPlay", "FiPlayCircle", "FiPause", "FiPauseCircle", "FiStopCircle",
        "FiSkipBack", "FiSkipForward", "FiFastForward", "FiRewind",
        "FiVolume", "FiVolume1", "FiVolume2", "FiVolumeX",
        "FiMusic", "FiHeadphones", "FiSpeaker", "FiFilm", "FiCamera",
        "FiImage", "FiDisc", "FiCast", "FiYoutube",
    ],
    "files & documents": [
        "FiFile", "FiFileText", "FiFilePlus", "FiFileMinus",
        "FiFolder", "FiFolderPlus", "FiFolderMinus",
        "FiClipboard", "FiArchive", "FiBook", "FiBookOpen", "FiBookmark",
        "FiPaperclip", "FiPrinter", "FiSave", "FiDownload", "FiUpload",
        "FiDownloadCloud", "FiUploadCloud", "FiCopy",
    ],
    "security & access": [
        "FiLock", "FiUnlock", "FiKey", "FiShield", "FiShieldOff",
        "FiEye", "FiEyeOff", "FiLogIn", "FiLogOut",
        "FiUserCheck", "FiUserX",
    ],
    "people & social": [
        "FiUser", "FiUsers", "FiUserPlus", "FiUserMinus",
        "FiSmile", "FiFrown", "FiMeh", "FiHeart",
        "FiThumbsUp", "FiThumbsDown", "FiShare", "FiShare2",
        "FiLinkedin", "FiFacebook", "FiTwitter", "FiInstagram",
    ],
    "status & feedback": [
        "FiCheck", "FiCheckCircle", "FiCheckSquare",
        "FiX", "FiXCircle", "FiXOctagon", "FiXSquare",
        "FiAlertCircle", "FiAlertTriangle", "FiAlertOctagon",
        "FiInfo", "FiHelpCircle", "FiBell", "FiBellOff",
    ],
    "navigation & direction": [
        "FiArrowUp", "FiArrowDown", "FiArrowLeft", "FiArrowRight",
        "FiArrowUpRight", "FiArrowUpLeft", "FiArrowDownRight", "FiArrowDownLeft",
        "FiChevronUp", "FiChevronDown", "FiChevronLeft", "FiChevronRight",
        "FiCornerUpRight", "FiCornerDownRight",
        "FiCompass", "FiNavigation", "FiNavigation2", "FiMap", "FiMapPin",
        "FiExternalLink", "FiLink", "FiLink2",
        "FiHome", "FiGlobe", "FiTarget", "FiCrosshair",
    ],
    "business & finance": [
        "FiBriefcase", "FiDollarSign", "FiCreditCard", "FiShoppingCart",
        "FiShoppingBag", "FiPackage", "FiTruck", "FiGift",
        "FiAward", "FiStar", "FiFlag", "FiTag",
    ],
    "tools & settings": [
        "FiSettings", "FiTool", "FiSliders", "FiFilter",
        "FiEdit", "FiEdit2", "FiEdit3", "FiPenTool", "FiScissors", "FiCrop",
        "FiSearch", "FiZoomIn", "FiZoomOut",
        "FiRefreshCw", "FiRefreshCcw", "FiRotateCw", "FiRotateCcw",
        "FiRepeat", "FiShuffle", "FiMove",
        "FiTrash", "FiTrash2", "FiDelete",
        "FiPlus", "FiPlusCircle", "FiMinus", "FiMinusCircle",
        "FiMaximize", "FiMinimize",
        "FiToggleLeft", "FiToggleRight", "FiPower",
    ],
    "layout & design": [
        "FiLayout", "FiLayers", "FiGrid", "FiColumns", "FiSidebar",
        "FiSquare", "FiCircle", "FiTriangle", "FiHexagon", "FiOctagon",
        "FiBox", "FiFeather", "FiFigma", "FiFramer",
        "FiAlignLeft", "FiAlignCenter", "FiAlignRight", "FiAlignJustify",
        "FiBold", "FiItalic", "FiUnderline", "FiType", "FiList",
        "FiMenu", "FiMoreHorizontal", "FiMoreVertical",
    ],
    "time & energy": [
        "FiClock", "FiWatch", "FiCalendar",
        "FiZap", "FiZapOff", "FiBattery", "FiBatteryCharging",
        "FiSun", "FiSunrise", "FiSunset", "FiMoon",
        "FiLoader",
    ],
    "nature & misc": [
        "FiDroplet", "FiCloudRain", "FiCloudSnow", "FiCloudDrizzle",
        "FiWind", "FiUmbrella", "FiThermometer", "FiAperture",
        "FiAnchor", "FiLifeBuoy", "FiSlash", "FiDivide",
        "FiMousePointer", "FiPocket",
    ],
}

# Flat list of all available icons (auto-generated from categories)
AVAILABLE_ICONS = sorted(set(
    icon for icons in ICON_CATEGORIES.values() for icon in icons
))

# ─── Default layout (matches production) ─────────────────────────────────────

DEFAULT_LAYOUT = {
    "left":   {"x": 80,   "y": 140, "width": 480, "height": 800},
    "center": {"x": 640,  "y": 0,   "width": 640, "height": 1080},
    "right":  {"x": 1360, "y": 140, "width": 480, "height": 800},
}


# ─── ffmpeg auto-discovery ────────────────────────────────────────────────────

_ffmpeg_path = None
_ffprobe_path = None


def find_ffmpeg():
    """Find ffmpeg/ffprobe, checking PATH first, then known Windows install locations."""
    global _ffmpeg_path, _ffprobe_path

    if _ffmpeg_path and _ffprobe_path:
        return

    # 1. Check if already in PATH
    ffmpeg_in_path = shutil.which("ffmpeg")
    if ffmpeg_in_path:
        _ffmpeg_path = ffmpeg_in_path
        _ffprobe_path = shutil.which("ffprobe") or ffmpeg_in_path.replace("ffmpeg", "ffprobe")
        return

    # 2. Search known Windows install locations
    search_roots = []
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        winget_dir = os.path.join(local_appdata, "Microsoft", "WinGet", "Packages")
        if os.path.isdir(winget_dir):
            search_roots.append(winget_dir)

    # Also check common locations
    for drive in ["C:", "D:"]:
        for folder in ["ffmpeg", "FFmpeg"]:
            candidate = os.path.join(drive, os.sep, folder, "bin", "ffmpeg.exe")
            if os.path.isfile(candidate):
                _ffmpeg_path = candidate
                _ffprobe_path = candidate.replace("ffmpeg.exe", "ffprobe.exe")
                return

    # Search WinGet packages
    for root in search_roots:
        for dirpath, dirnames, filenames in os.walk(root):
            if "ffmpeg.exe" in filenames:
                _ffmpeg_path = os.path.join(dirpath, "ffmpeg.exe")
                _ffprobe_path = os.path.join(dirpath, "ffprobe.exe")
                print(f"  [auto] Found ffmpeg at: {_ffmpeg_path}")
                return

    raise RuntimeError(
        "ffmpeg not found. Install with: winget install Gyan.FFmpeg\n"
        "Or add ffmpeg to your PATH."
    )


def ffmpeg_cmd():
    find_ffmpeg()
    return _ffmpeg_path


def ffprobe_cmd():
    find_ffmpeg()
    return _ffprobe_path


# ─── Step 1: Extract audio ───────────────────────────────────────────────────

def extract_audio(video_path: Path) -> Path:
    """Extract audio from video to mono 16kHz MP3 using ffmpeg."""
    stem = video_path.stem
    audio_path = TRANSCRIPTS_DIR / f"{stem}_audio.mp3"

    if audio_path.exists():
        print(f"  [cache] Audio already exists: {audio_path.name}")
        return audio_path

    print(f"  Extracting audio from {video_path.name}...")
    cmd = [
        ffmpeg_cmd(), "-i", str(video_path),
        "-ar", "16000", "-ac", "1", "-map", "a",
        "-y",  # overwrite
        str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ffmpeg stderr: {result.stderr[-500:]}", file=sys.stderr)
        raise RuntimeError("ffmpeg failed.")

    size_mb = audio_path.stat().st_size / (1024 * 1024)
    print(f"  Audio extracted: {audio_path.name} ({size_mb:.1f} MB)")
    return audio_path


# ─── Step 2: Transcribe with Groq Whisper ────────────────────────────────────

def transcribe_audio(client: Groq, audio_path: Path, force: bool = False) -> list[dict]:
    """Transcribe audio using Groq Whisper API. Returns list of segments."""
    stem = audio_path.stem.replace("_audio", "")
    transcript_path = TRANSCRIPTS_DIR / f"{stem}_transcript.json"

    if transcript_path.exists() and not force:
        print(f"  [cache] Transcript exists: {transcript_path.name}")
        with open(transcript_path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"  Transcribing with Groq Whisper...")
    file_size = audio_path.stat().st_size / (1024 * 1024)
    if file_size > 25:
        raise RuntimeError(f"Audio file too large ({file_size:.1f} MB). Groq limit is 25 MB.")

    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            file=(audio_path.name, audio_file),
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
        )

    # Extract segments with timestamps
    segments = []
    for seg in response.segments:
        segments.append({
            "text": seg["text"].strip() if isinstance(seg, dict) else seg.text.strip(),
            "start": round(seg["start"] if isinstance(seg, dict) else seg.start, 2),
            "end": round(seg["end"] if isinstance(seg, dict) else seg.end, 2),
        })

    # Save cache
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)

    print(f"  Transcription complete: {len(segments)} segments, saved to {transcript_path.name}")
    return segments


# ─── Step 3: Generate items with Groq LLM ────────────────────────────────────

def get_video_duration(video_path: Path) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        ffprobe_cmd(), "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("ffprobe failed.")
    return float(result.stdout.strip())


def format_transcript_for_prompt(segments: list[dict]) -> str:
    """Format transcript segments as readable text with timestamps."""
    lines = []
    for seg in segments:
        lines.append(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
    return "\n".join(lines)


def generate_items(client: Groq, segments: list[dict], duration: float) -> list[dict]:
    """Use Groq LLM to generate editorial highlight items from transcript."""
    print(f"  Generating highlights with Groq LLM...")

    # Load prompt template
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    # Load example JSON (items only)
    with open(EXAMPLE_JSON_PATH, "r", encoding="utf-8") as f:
        example_data = json.load(f)
    example_items = json.dumps(example_data["items"], ensure_ascii=False, indent=2)

    # Build prompt
    transcript_text = format_transcript_for_prompt(segments)
    # Build categorized icon list so LLM can pick semantically
    icon_lines = []
    for category, icons in ICON_CATEGORIES.items():
        icon_lines.append(f"  {category}: {', '.join(icons)}")
    icon_list = "\n".join(icon_lines)

    prompt = template.format(
        icon_list=icon_list,
        example_json=example_items,
        duration=int(duration),
        transcript=transcript_text,
    )

    # Call LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a JSON generator. Output only valid JSON arrays, no markdown fences, no explanation."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=4000,
    )

    raw = response.choices[0].message.content.strip()

    # Clean markdown fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
        raw = re.sub(r"\n?```\s*$", "", raw)

    items = json.loads(raw)

    # Post-process: enforce animation rules
    for item in items:
        col = item.get("column", "left")
        item["animationIn"] = "slideRightFade" if col == "left" else "slideLeftFade"
        item["animationOut"] = "fadeOut"
        if "verticalAlign" not in item:
            item["verticalAlign"] = "center"
        # Validate icon exists
        if "icon" in item and item["icon"] not in AVAILABLE_ICONS:
            item.pop("icon")

    print(f"  Generated {len(items)} items")
    return items


# ─── Step 4: Assemble final JSON ─────────────────────────────────────────────

def assemble_json(video_filename: str, duration: float, items: list[dict]) -> dict:
    """Build the complete VideoLayout JSON structure."""
    return {
        "videoSrc": video_filename,
        "canvas": {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "durationInSeconds": int(duration),
        },
        "layout": DEFAULT_LAYOUT,
        "items": items,
    }


# ─── Step 5: Auto-register in Root.tsx ────────────────────────────────────────

def slugify(name: str) -> str:
    """Convert filename to a clean slug for JSON output."""
    name = name.lower().strip()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_]+", "-", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


def slug_to_varname(slug: str) -> str:
    """Convert a slug to a valid JS variable name: 'mi-video' -> 'miVideo'."""
    parts = slug.split("-")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def slug_to_composition_id(slug: str) -> str:
    """Convert a slug to PascalCase composition ID: 'mi-video' -> 'MiVideo'."""
    return "".join(p.capitalize() for p in slug.split("-"))


def register_in_root_tsx(json_filename: str, slug: str):
    """Auto-register a new composition in Root.tsx."""
    root_path = ROOT_TSX_PATH
    if not root_path.exists():
        print(f"  [skip] Root.tsx not found at {root_path}")
        return False

    content = root_path.read_text(encoding="utf-8")

    # Check if already registered
    if json_filename in content:
        print(f"  [skip] '{json_filename}' already registered in Root.tsx")
        return False

    var_name = slug_to_varname(slug)
    comp_id = slug_to_composition_id(slug)
    import_line = f'import {var_name}Data from "./data/{json_filename}";'

    # Build the composition block
    cast_line = f"  const {var_name} = {var_name}Data as VideoLayout;"
    comp_block = f"""      <TypedComposition
        id="{comp_id}"
        component={{AvatarSideTitles}}
        width={{{var_name}.canvas.width}}
        height={{{var_name}.canvas.height}}
        fps={{{var_name}.canvas.fps}}
        durationInFrames={{{var_name}.canvas.durationInSeconds * {var_name}.canvas.fps}}
        defaultProps={{{var_name}}}
      />"""

    # 1. Add import after the last existing data import
    # Find the last import from "./data/..."
    import_pattern = r'(import .+ from "\./data/.+";)\n'
    matches = list(re.finditer(import_pattern, content))
    if matches:
        last_match = matches[-1]
        insert_pos = last_match.end()
        content = content[:insert_pos] + import_line + "\n" + content[insert_pos:]
    else:
        # Fallback: add after the layout import
        layout_import = 'import type { VideoLayout } from "./lib/layout";'
        content = content.replace(layout_import, layout_import + "\n" + import_line)

    # 2. Add the const cast before "return ("
    return_pattern = r'(\n  return \(\n)'
    content = re.sub(
        return_pattern,
        f"\n{cast_line}\n\n  return (\n",
        content,
        count=1,
    )

    # 3. Add composition block after the first <> (opening fragment)
    fragment_pattern = r'(<>\n)'
    content = re.sub(
        fragment_pattern,
        f"<>\n{comp_block}\n",
        content,
        count=1,
    )

    root_path.write_text(content, encoding="utf-8")
    print(f"  [ok] Registered composition '{comp_id}' in Root.tsx")
    return True


# ─── Pipeline for a single video ─────────────────────────────────────────────

def process_video(client: Groq, video_path: Path, output_name: str | None = None,
                  force_transcribe: bool = False, duration_override: float | None = None,
                  auto_register: bool = True) -> Path:
    """Run the full pipeline for a single video. Returns the output JSON path."""
    video_filename = video_path.name
    stem = video_path.stem
    slug = output_name or slugify(stem)

    print(f"\n{'='*60}")
    print(f"  Pipeline: {video_filename}")
    print(f"{'='*60}\n")

    # Step 1: Extract audio
    print("[1/5] Extracting audio...")
    audio_path = extract_audio(video_path)

    # Step 2: Transcribe
    print("\n[2/5] Transcribing audio...")
    segments = transcribe_audio(client, audio_path, force=force_transcribe)

    # Get duration
    if duration_override:
        duration = duration_override
    else:
        print("\n[2.5] Getting video duration...")
        duration = get_video_duration(video_path)
    print(f"  Duration: {duration:.1f}s")

    # Step 3: Generate items
    print("\n[3/5] Generating editorial highlights...")
    items = generate_items(client, segments, duration)

    # Step 4: Assemble and write JSON
    print("\n[4/5] Assembling JSON...")
    layout_json = assemble_json(video_filename, duration, items)

    json_filename = f"{slug}.json"
    output_path = DATA_DIR / json_filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(layout_json, f, ensure_ascii=False, indent=2)
    print(f"  JSON written to: {output_path}")
    print(f"  Items: {len(items)}")

    # Step 5: Auto-register in Root.tsx
    if auto_register:
        print("\n[5/5] Registering in Root.tsx...")
        register_in_root_tsx(json_filename, slug)
    else:
        print("\n[5/5] Skipping Root.tsx registration (--no-register)")

    comp_id = slug_to_composition_id(slug)
    print(f"\n  Ready! Run 'npm start' and select '{comp_id}' in Remotion Studio.")
    print(f"  Or render: npx remotion render {comp_id} out/{slug}.mp4")
    print(f"\n{'='*60}\n")

    return output_path


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate motion graphics JSON from video files using AI."
    )

    # Input: either a single video or a batch folder
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--video", help="Path to a single MP4 video file")
    input_group.add_argument("--batch", help="Path to a folder with MP4 videos (processes all)")

    parser.add_argument("--output", help="Output JSON filename (without extension). Only for --video.")
    parser.add_argument("--force-transcribe", action="store_true",
                        help="Re-transcribe even if cache exists")
    parser.add_argument("--duration", type=float,
                        help="Video duration in seconds (skip ffprobe). Only for --video.")
    parser.add_argument("--no-register", action="store_true",
                        help="Don't auto-register compositions in Root.tsx")

    args = parser.parse_args()

    # Load env
    load_dotenv(SCRIPT_DIR / ".env")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not set. Copy .env.example to .env and add your key.",
              file=sys.stderr)
        sys.exit(1)

    # Use custom httpx client to handle SSL cert issues on Windows/corporate networks
    http_client = httpx.Client(verify=False)
    client = Groq(api_key=api_key, http_client=http_client)

    # Verify ffmpeg is available
    try:
        find_ffmpeg()
        print(f"[ok] ffmpeg found: {_ffmpeg_path}")
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    auto_register = not args.no_register

    if args.video:
        # ─── Single video mode ───
        video_path = Path(args.video).resolve()
        if not video_path.exists():
            print(f"ERROR: Video not found: {video_path}", file=sys.stderr)
            sys.exit(1)

        process_video(
            client, video_path,
            output_name=args.output,
            force_transcribe=args.force_transcribe,
            duration_override=args.duration,
            auto_register=auto_register,
        )

    elif args.batch:
        # ─── Batch mode ───
        batch_dir = Path(args.batch).resolve()
        if not batch_dir.is_dir():
            print(f"ERROR: Not a directory: {batch_dir}", file=sys.stderr)
            sys.exit(1)

        # Find all MP4 files
        mp4_files = sorted(batch_dir.glob("*.mp4"))
        if not mp4_files:
            print(f"ERROR: No MP4 files found in {batch_dir}", file=sys.stderr)
            sys.exit(1)

        print(f"\n{'#'*60}")
        print(f"  BATCH MODE: {len(mp4_files)} videos found")
        print(f"{'#'*60}")
        for i, vp in enumerate(mp4_files, 1):
            print(f"  {i}. {vp.name}")
        print()

        results = []
        for i, video_path in enumerate(mp4_files, 1):
            print(f"\n{'#'*60}")
            print(f"  VIDEO {i}/{len(mp4_files)}")
            print(f"{'#'*60}")
            try:
                output_path = process_video(
                    client, video_path,
                    force_transcribe=args.force_transcribe,
                    auto_register=auto_register,
                )
                results.append((video_path.name, "OK", output_path.name))
            except Exception as e:
                print(f"\n  ERROR processing {video_path.name}: {e}", file=sys.stderr)
                results.append((video_path.name, "FAILED", str(e)[:60]))

        # Print summary
        print(f"\n\n{'#'*60}")
        print(f"  BATCH SUMMARY")
        print(f"{'#'*60}\n")
        ok_count = sum(1 for _, status, _ in results if status == "OK")
        fail_count = len(results) - ok_count
        for video_name, status, detail in results:
            icon = "[ok]" if status == "OK" else "[FAIL]"
            print(f"  {icon} {video_name} -> {detail}")
        print(f"\n  Total: {ok_count} OK, {fail_count} failed out of {len(results)}")
        print(f"\n  Run 'npm start' to preview all compositions in Remotion Studio.")
        print(f"\n{'#'*60}\n")


if __name__ == "__main__":
    main()
