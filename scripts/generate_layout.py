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


def validate_no_overlap(items: list[dict]) -> list[str]:
    """Check that no fullscreen overlay overlaps with titles or other overlays. Returns error messages."""
    errors = []
    fullscreen = [i for i in items if i.get("type") in ("image", "clip")]
    titles = [i for i in items if i.get("type") not in ("image", "clip")]
    buffer = 2.0

    # Titles vs fullscreen overlays
    for fs in fullscreen:
        for title in titles:
            if title["start"] < fs["end"] + buffer and title["end"] > fs["start"] - buffer:
                errors.append(
                    f'Overlap: {fs["type"]} "{fs["id"]}" [{fs["start"]}-{fs["end"]}s] '
                    f'conflicts with title "{title["id"]}" [{title["start"]}-{title["end"]}s]'
                )

    # Fullscreen overlays vs each other
    for i, a in enumerate(fullscreen):
        for b in fullscreen[i + 1:]:
            if a["start"] < b["end"] + buffer and a["end"] > b["start"] - buffer:
                errors.append(
                    f'Overlap: {a["type"]} "{a["id"]}" [{a["start"]}-{a["end"]}s] '
                    f'conflicts with {b["type"]} "{b["id"]}" [{b["start"]}-{b["end"]}s]'
                )

    return errors


def auto_fix_overlaps(items: list[dict]) -> list[dict]:
    """Remove title items that conflict with fullscreen overlays (overlays win). Uses 2s buffer."""
    fullscreen = [i for i in items if i.get("type") in ("image", "clip")]
    if not fullscreen:
        return items

    result = []
    removed = 0
    for item in items:
        if item.get("type") in ("image", "clip"):
            result.append(item)
            continue
        # Check if this title overlaps any fullscreen overlay (with 2s buffer)
        overlaps = False
        for fs in fullscreen:
            buffer = 2.0
            if item["start"] < (fs["end"] + buffer) and item["end"] > (fs["start"] - buffer):
                overlaps = True
                break
        if overlaps:
            removed += 1
        else:
            result.append(item)

    if removed > 0:
        print(f"  [fix] Removed {removed} title(s) that overlapped with fullscreen overlays")

    return result


def generate_items(client: Groq, segments: list[dict], duration: float) -> list[dict]:
    """Use Groq LLM to generate editorial highlight items from transcript."""
    print(f"  Generating highlights with Groq LLM...")

    # Load prompt template
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    # Load example JSON (optional — improves LLM output but not required)
    example_section = ""
    if EXAMPLE_JSON_PATH.exists():
        try:
            with open(EXAMPLE_JSON_PATH, "r", encoding="utf-8") as f:
                example_data = json.load(f)
            example_items = json.dumps(example_data["items"], ensure_ascii=False, indent=2)
            example_section = f"\n## Production Example\nHere is a real production example for reference:\n{example_items}\n"
        except Exception as e:
            print(f"  [warn] Could not load example JSON: {e}")

    # Build prompt
    transcript_text = format_transcript_for_prompt(segments)
    # Build categorized icon list so LLM can pick semantically
    icon_lines = []
    for category, icons in ICON_CATEGORIES.items():
        icon_lines.append(f"  {category}: {', '.join(icons)}")
    icon_list = "\n".join(icon_lines)

    overlay_seconds = int(duration * 0.7)

    prompt = template.format(
        icon_list=icon_list,
        example_json=example_section,
        duration=int(duration),
        overlay_seconds=overlay_seconds,
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

    # Post-process: infer type from id prefix if missing, enforce defaults
    for item in items:
        # Infer type from id prefix when LLM forgets the type field
        if "type" not in item:
            item_id = item.get("id", "")
            if item_id.startswith("img"):
                item["type"] = "image"
            elif item_id.startswith("clip"):
                item["type"] = "clip"
            # Also detect by presence of prompt fields
            elif "imagePrompt" in item:
                item["type"] = "image"
            elif "clipPrompt" in item:
                item["type"] = "clip"

        if item.get("type") == "image":
            item["src"] = "NEEDS_IMAGE"
            item["animationIn"] = "fadeIn"
            item["animationOut"] = "fadeOut"
            item["display"] = item.get("display", "fullscreen")
            # Remove title-only fields that LLM may have added
            for key in ("column", "verticalAlign", "variant", "icon"):
                item.pop(key, None)
        elif item.get("type") == "clip":
            item["src"] = "NEEDS_CLIP"
            item["display"] = "fullscreen"
            item["animationIn"] = "fadeIn"
            item["animationOut"] = "fadeOut"
            # Remove title-only fields
            for key in ("column", "verticalAlign", "variant", "icon"):
                item.pop(key, None)
        else:
            # Title items
            col = item.get("column", "left")
            item["animationIn"] = "slideRightFade" if col == "left" else "slideLeftFade"
            item["animationOut"] = "fadeOut"
            if "verticalAlign" not in item:
                item["verticalAlign"] = "center"
            if "icon" in item and item["icon"] not in AVAILABLE_ICONS:
                item.pop("icon")

    # Validate and auto-fix overlaps (fullscreen overlays win over titles)
    items = auto_fix_overlaps(items)

    # Sort all items by start time
    items.sort(key=lambda i: i["start"])

    n_images = len([i for i in items if i.get("type") == "image"])
    n_clips = len([i for i in items if i.get("type") == "clip"])
    n_titles = len([i for i in items if i.get("type") not in ("image", "clip")])
    print(f"  Generated {len(items)} items ({n_images} images, {n_clips} clips, {n_titles} titles)")
    return items


# ─── Step 4: Assemble final JSON ─────────────────────────────────────────────

def compute_video_src(video_path: Path) -> str:
    """Compute relative path from public/ directory for videoSrc.
    If the video is inside public/, returns the relative path.
    Otherwise returns just the filename (legacy behavior).
    """
    public_dir = PROJECT_DIR / "public"
    try:
        rel = video_path.resolve().relative_to(public_dir.resolve())
        # Use forward slashes for JSON/web compatibility
        return str(rel).replace("\\", "/")
    except ValueError:
        return video_path.name


def assemble_json(video_src: str, duration: float, items: list[dict]) -> dict:
    """Build the complete VideoLayout JSON structure."""
    return {
        "videoSrc": video_src,
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


# ─── Interactive mode helpers ─────────────────────────────────────────────────

def get_transcript_in_range(segments: list[dict], start: float, end: float) -> str:
    """Get transcript text for a given time range."""
    texts = []
    for seg in segments:
        if seg["end"] > start and seg["start"] < end:
            texts.append(seg["text"])
    return " ".join(texts)


def generate_image_prompt(client: Groq, transcript_excerpt: str, start: float, end: float,
                          designer_notes: str = "") -> dict:
    """Use LLM to generate an imagePrompt for a specific transcript section."""
    notes_section = ""
    if designer_notes:
        notes_section = f"""
The designer has specifically requested:
"{designer_notes}"
IMPORTANT: Follow the designer's instructions closely. Include ALL specific data, numbers, percentages, and details they mention or that appear in the transcript."""

    prompt = f"""Given this excerpt from an educational video transcript (timestamps {start:.0f}s-{end:.0f}s):

"{transcript_excerpt}"
{notes_section}

Generate a JSON object for an image overlay with this field:
- "imagePrompt": 2-3 sentences describing the ideal image for this content. Write it as an image generation prompt optimized for DALL-E or Midjourney.

VISUAL STYLE (MANDATORY — the image will overlay a premium corporate avatar video with warm amber lighting and dark wood tones):
- Dark warm background (#1a1a2e to #2d1b00 gradient), amber/golden accent colors, soft warm lighting with subtle glow effects
- Premium corporate infographic style, cinematic quality, NO white backgrounds, NO clip-art
- Sans-serif typography (Roboto-style), warm palette: amber (#F59E0B), gold (#D4A574), warm white (#FFF8F0), soft teal (#5EEAD4) accent
- NEVER flat textbook style or bright primary colors without warm undertones

TEXT MINIMIZATION (CRITICAL — viewer has only 5-8 seconds):
- MINIMIZE text. Prefer icons, color coding, proportional sizing, and spatial layout over labels.
- When data/numbers are essential, show them LARGE and PROMINENT with single-word labels only.
- Max 2-3 words per label. No sentences, no paragraphs, no long descriptions in the image.
- The image must be understandable at a glance.
- ALL text that appears MUST be in the SAME LANGUAGE as the transcript.

CONTENT RULES:
- Include specific numbers and data from the transcript (show as large visual elements, not as text blocks)
- Be specific about chart type, layout, and composition
- The prompt must be self-contained

Return ONLY valid JSON, no markdown, no explanation. Example:
{{"imagePrompt": "Grafico de barras horizontal — emisiones CO2 por sector: electricidad 32%, transporte 16%, manufactura 13%, industria 10%. Numeros grandes y prominentes en cada barra, etiquetas de una sola palabra. Barras con gradiente ambar a dorado sobre fondo oscuro (#1a1a2e), brillo sutil en bordes, estilo infografico corporativo premium, tipografia sans-serif, calidad cinematografica."}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a JSON generator. Output only valid JSON, no markdown fences."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=500,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
        raw = re.sub(r"\n?```\s*$", "", raw)

    return json.loads(raw)


def display_timeline(items: list[dict], segments: list[dict], duration: float):
    """Display current items and transcript gaps where images could be added."""
    print(f"\n{'-'*70}")
    print(f"  TIMELINE (video: {duration:.0f}s)")
    print(f"{'-'*70}\n")

    # Sort items by start
    sorted_items = sorted(items, key=lambda i: i["start"])

    for item in sorted_items:
        item_type = item.get("type", "title")
        if item_type == "image":
            status = "NEEDS_IMAGE" if item["src"] == "NEEDS_IMAGE" else item["src"]
            print(f"  [{item['start']:6.1f}s - {item['end']:6.1f}s]  IMG  {item['id']:6s}  {item.get('caption', '—'):30s}  ({status})")
        elif item_type == "clip":
            status = "NEEDS_CLIP" if item["src"] == "NEEDS_CLIP" else item["src"]
            prompt_preview = (item.get("clipPrompt", "—") or "—")[:30]
            print(f"  [{item['start']:6.1f}s - {item['end']:6.1f}s]  CLIP {item['id']:6s}  {prompt_preview:30s}  ({status})")
        else:
            icon = item.get("icon", "—")
            print(f"  [{item['start']:6.1f}s - {item['end']:6.1f}s]  TXT  {item['id']:6s}  {item['text']:30s}  {icon}")

    # Show gaps > 10s where images could go
    print(f"\n{'-'*70}")
    print(f"  GAPS > 10s (good spots for images):")
    print(f"{'-'*70}\n")

    prev_end = 0
    gaps_found = False
    for item in sorted_items:
        gap = item["start"] - prev_end
        if gap > 10:
            excerpt = get_transcript_in_range(segments, prev_end, item["start"])
            excerpt_short = excerpt[:120] + "..." if len(excerpt) > 120 else excerpt
            print(f"  GAP [{prev_end:.0f}s - {item['start']:.0f}s] ({gap:.0f}s)")
            print(f"      \"{excerpt_short}\"")
            print()
            gaps_found = True
        prev_end = item["end"]

    # Check gap after last item
    if sorted_items:
        last_end = sorted_items[-1]["end"]
        remaining = duration - last_end
        if remaining > 10:
            excerpt = get_transcript_in_range(segments, last_end, duration)
            excerpt_short = excerpt[:120] + "..." if len(excerpt) > 120 else excerpt
            print(f"  GAP [{last_end:.0f}s - {duration:.0f}s] ({remaining:.0f}s)")
            print(f"      \"{excerpt_short}\"")
            print()
            gaps_found = True

    if not gaps_found:
        print("  (no large gaps found)")

    print(f"{'-'*70}")


def display_transcript_range(segments: list[dict], start: float, end: float):
    """Show the transcript for a specific time range, splitting long segments."""
    print(f"\n  Transcript [{start:.0f}s - {end:.0f}s]:")
    print(f"  {'-'*50}")
    found = False
    for seg in segments:
        seg_start = seg["start"]
        seg_end = seg["end"]
        # Include segment if it overlaps with the requested range
        if seg_end > start and seg_start < end:
            text = seg["text"].strip()
            # If segment is much larger than requested range, show full text
            # but mark the relevant portion
            marker = ""
            if seg_start < start - 5 or seg_end > end + 5:
                marker = " (partial overlap)"
            print(f"  [{seg_start:6.1f}s - {seg_end:6.1f}s]{marker}")
            # Word-wrap long text for readability
            words = text.split()
            line = "    "
            for word in words:
                if len(line) + len(word) + 1 > 75:
                    print(line)
                    line = "    " + word
                else:
                    line += " " + word if line.strip() else "    " + word
            if line.strip():
                print(line)
            print()
            found = True
    if not found:
        print("  (no transcript in this range)")
    print()


def generate_titles_for_range(client: Groq, segments: list[dict],
                              start: float, end: float,
                              existing_items: list[dict]) -> list[dict]:
    """Use Groq LLM to generate title items for a specific time range."""
    excerpt = get_transcript_in_range(segments, start, end)
    if not excerpt.strip():
        print("  No transcript found in this range.")
        return []

    # Figure out what column the next title should start on
    titles_before = sorted(
        [i for i in existing_items if i.get("type") != "image" and i["end"] <= start],
        key=lambda i: i["start"],
    )
    last_col = titles_before[-1]["column"] if titles_before else "right"
    first_col = "right" if last_col == "left" else "left"

    prompt = f"""Given this excerpt from an educational video transcript ({start:.0f}s-{end:.0f}s):

"{excerpt}"

Generate 2-4 title highlight items to fill this time range. Each title captures one key concept.

RULES:
- Text must be short (max 8 words), punchy, in the SAME LANGUAGE as the transcript
- Alternate columns starting with "{first_col}": {first_col}, {"left" if first_col == "right" else "right"}, ...
- Each title visible 4-5 seconds
- Leave 2+ second gaps between items
- First item starts at or after {start:.0f}s
- Last item ends at or before {end:.0f}s
- Choose icons from: FiDatabase, FiBarChart, FiTrendingUp, FiZap, FiSettings, FiUsers, FiGlobe, FiLayers, FiShield, FiCode, FiCloud, FiCpu, FiStar, FiTarget, FiMap, FiList, FiGrid, FiActivity, FiInfo, FiCheckCircle, FiAlertCircle, FiArrowRight, FiBriefcase, FiDollarSign, FiCalendar, FiBookOpen, FiAward

Return ONLY a valid JSON array. No markdown, no explanation."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a JSON generator. Output only valid JSON arrays, no markdown fences."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
        raw = re.sub(r"\n?```\s*$", "", raw)

    new_items = json.loads(raw)

    # Post-process: enforce animation rules
    for item in new_items:
        col = item.get("column", "left")
        item["animationIn"] = "slideRightFade" if col == "left" else "slideLeftFade"
        item["animationOut"] = "fadeOut"
        if "verticalAlign" not in item:
            item["verticalAlign"] = "center"
        if "variant" not in item:
            item["variant"] = "headline"
        if "icon" in item and item["icon"] not in AVAILABLE_ICONS:
            item.pop("icon")

    return new_items


def interactive_session(client: Groq, items: list[dict], segments: list[dict],
                        duration: float) -> list[dict]:
    """Interactive CLI to review items, add titles/images, and fill gaps."""
    print(f"\n{'='*70}")
    print(f"  INTERACTIVE EDITOR")
    print(f"  Review items, add titles/images, fill gaps.")
    print(f"{'='*70}")
    print()
    print("  Commands:")
    print("    show                        — Show timeline + gaps")
    print("    transcript <start> <end>    — Show transcript for time range")
    print("    add-title <start> <end> <text> [left|right]  — Add a title manually")
    print("    add-image <start> <end> [fullscreen|pip]     — Add image with AI prompt")
    print("    fill-gaps                   — AI generates titles for all gaps > 10s")
    print("    fill <start> <end>          — AI generates titles for a specific range")
    print("    edit <id> <field> <value>   — Edit a field (text, icon, start, end)")
    print("    remove <id>                 — Remove an item by ID")
    print("    edit-prompt <id>            — Re-generate imagePrompt for an image")
    print("    done                        — Save and continue")
    print()

    # Show timeline first
    display_timeline(items, segments, duration)

    while True:
        try:
            cmd = input("\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting interactive mode.")
            break

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0].lower()

        if action == "done":
            print("  Saving...")
            break

        elif action == "show":
            display_timeline(items, segments, duration)

        elif action == "transcript" and len(parts) >= 3:
            try:
                t_start = float(parts[1])
                t_end = float(parts[2])
                display_transcript_range(segments, t_start, t_end)
            except ValueError:
                print("  Usage: transcript <start_seconds> <end_seconds>")

        # ── add-title: manual title ──────────────────────────────────────
        elif action == "add-title" and len(parts) >= 4:
            try:
                t_start = float(parts[1])
                t_end = float(parts[2])
                # Text is everything after start/end, optionally ending with left|right
                remaining = parts[3:]
                if remaining[-1] in ("left", "right"):
                    col = remaining[-1]
                    text = " ".join(remaining[:-1])
                else:
                    # Auto-detect column based on last title
                    titles_before = sorted(
                        [i for i in items if i.get("type") != "image" and i["end"] <= t_start],
                        key=lambda i: i["start"],
                    )
                    last_col = titles_before[-1]["column"] if titles_before else "right"
                    col = "right" if last_col == "left" else "left"
                    text = " ".join(remaining)

                if t_end - t_start < 2:
                    print("  Title should be at least 2 seconds")
                    continue

                # Auto-assign ID
                existing_h = [i for i in items if i.get("type") != "image"]
                h_num = len(existing_h) + 1
                new_id = f"h{h_num}"

                new_item = {
                    "id": new_id,
                    "text": text,
                    "start": t_start,
                    "end": t_end,
                    "column": col,
                    "verticalAlign": "center",
                    "variant": "headline",
                    "animationIn": "slideRightFade" if col == "left" else "slideLeftFade",
                    "animationOut": "fadeOut",
                }

                print(f"  Add icon? (enter icon name or press Enter to skip):")
                icon_input = input("  Icon: ").strip()
                if icon_input and icon_input in AVAILABLE_ICONS:
                    new_item["icon"] = icon_input
                elif icon_input:
                    print(f"  Icon '{icon_input}' not found, skipping")

                items.append(new_item)
                items.sort(key=lambda i: i["start"])
                print(f"  [ok] Added title '{new_id}': \"{text}\" [{t_start:.0f}s-{t_end:.0f}s] ({col})")

            except ValueError:
                print("  Usage: add-title <start> <end> <text> [left|right]")

        # ── fill-gaps: AI fills all gaps > 10s ───────────────────────────
        elif action == "fill-gaps":
            sorted_items = sorted(items, key=lambda i: i["start"])
            gaps = []

            prev_end = 0
            for item in sorted_items:
                gap = item["start"] - prev_end
                if gap > 10:
                    gaps.append((prev_end + 2, item["start"] - 2))
                prev_end = max(prev_end, item["end"])

            # Check gap after last item
            if sorted_items:
                last_end = sorted_items[-1]["end"]
                remaining = duration - last_end
                if remaining > 10:
                    gaps.append((last_end + 2, duration - 8))

            if not gaps:
                print("  No gaps > 10s found.")
                continue

            print(f"  Found {len(gaps)} gap(s) to fill:")
            for g_start, g_end in gaps:
                print(f"    [{g_start:.0f}s - {g_end:.0f}s] ({g_end - g_start:.0f}s)")

            confirm = input("\n  Generate titles for all gaps? (y/n): ").strip().lower()
            if confirm not in ("y", "yes", "si", "s"):
                print("  Skipped.")
                continue

            total_added = 0
            for g_start, g_end in gaps:
                print(f"\n  Filling gap [{g_start:.0f}s - {g_end:.0f}s]...")
                try:
                    new_titles = generate_titles_for_range(client, segments, g_start, g_end, items)
                    if new_titles:
                        for nt in new_titles:
                            existing_h = [i for i in items if i.get("type") != "image"]
                            nt["id"] = f"h{len(existing_h) + 1}"
                            items.append(nt)
                            total_added += 1
                            print(f"    + {nt['id']}: \"{nt['text']}\" [{nt['start']:.0f}s-{nt['end']:.0f}s]")
                except Exception as e:
                    print(f"    Error: {e}")

            items.sort(key=lambda i: i["start"])
            print(f"\n  [ok] Added {total_added} title(s)")
            display_timeline(items, segments, duration)

        # ── fill <start> <end>: AI fills a specific range ────────────────
        elif action == "fill" and len(parts) >= 3:
            try:
                f_start = float(parts[1])
                f_end = float(parts[2])

                if f_end - f_start < 5:
                    print("  Range should be at least 5 seconds")
                    continue

                display_transcript_range(segments, f_start, f_end)
                print(f"  Generating titles for [{f_start:.0f}s - {f_end:.0f}s]...")

                new_titles = generate_titles_for_range(client, segments, f_start, f_end, items)
                if not new_titles:
                    print("  No titles generated.")
                    continue

                print(f"\n  AI suggests {len(new_titles)} title(s):")
                for nt in new_titles:
                    print(f"    \"{nt['text']}\" [{nt['start']:.0f}s-{nt['end']:.0f}s] ({nt.get('column','?')}) icon:{nt.get('icon','—')}")

                confirm = input("\n  Add these titles? (y/n): ").strip().lower()
                if confirm in ("y", "yes", "si", "s"):
                    for nt in new_titles:
                        existing_h = [i for i in items if i.get("type") != "image"]
                        nt["id"] = f"h{len(existing_h) + 1}"
                        items.append(nt)
                    items.sort(key=lambda i: i["start"])
                    print(f"  [ok] Added {len(new_titles)} title(s)")
                else:
                    print("  Skipped.")

            except ValueError:
                print("  Usage: fill <start_seconds> <end_seconds>")

        # ── edit <id> <field> <value>: modify any item field ─────────────
        elif action == "edit" and len(parts) >= 4:
            target_id = parts[1]
            field = parts[2]
            value = " ".join(parts[3:])

            target = next((i for i in items if i["id"] == target_id), None)
            if not target:
                print(f"  Item '{target_id}' not found")
                continue

            editable = {"text", "icon", "start", "end", "column", "variant", "fontSize", "display", "caption"}
            if field not in editable:
                print(f"  Editable fields: {', '.join(sorted(editable))}")
                continue

            # Type conversion
            if field in ("start", "end", "fontSize"):
                try:
                    value = float(value)
                    if field == "fontSize":
                        value = int(value)
                except ValueError:
                    print(f"  {field} must be a number")
                    continue

            old_val = target.get(field, "(none)")
            target[field] = value

            # Auto-fix animation direction if column changed
            if field == "column" and target.get("type") != "image":
                target["animationIn"] = "slideRightFade" if value == "left" else "slideLeftFade"

            # Re-sort if timing changed
            if field in ("start", "end"):
                items.sort(key=lambda i: i["start"])

            print(f"  [ok] {target_id}.{field}: {old_val} -> {value}")

        # ── add-image ────────────────────────────────────────────────────
        elif action == "add-image" and len(parts) >= 3:
            try:
                img_start = float(parts[1])
                img_end = float(parts[2])
                display_mode = parts[3] if len(parts) >= 4 else "fullscreen"

                if display_mode not in ("fullscreen", "pip"):
                    print("  Display must be 'fullscreen' or 'pip'")
                    continue

                if img_end - img_start < 3:
                    print("  Image should be at least 3 seconds")
                    continue

                # Show what transcript is in this range
                display_transcript_range(segments, img_start, img_end)
                excerpt = get_transcript_in_range(segments, img_start - 5, img_end + 5)

                if not excerpt.strip():
                    print("  Warning: no transcript found in this range. Generating prompt anyway...")
                    excerpt = f"Content at {img_start:.0f}s-{img_end:.0f}s of an educational video"

                # Ask designer for notes
                print("  Describe what you want to see (or press Enter for auto):")
                print("  Example: 'bar chart with emission percentages per sector'")
                designer_notes = input("  Notes: ").strip()

                print("  Generating imagePrompt with AI...")
                result = generate_image_prompt(client, excerpt, img_start, img_end, designer_notes)

                # Build image item
                existing_imgs = [i for i in items if i.get("type") == "image"]
                img_num = len(existing_imgs) + 1
                new_item = {
                    "type": "image",
                    "id": f"img{img_num}",
                    "src": "NEEDS_IMAGE",
                    "imagePrompt": result.get("imagePrompt", ""),
                    "start": img_start,
                    "end": img_end,
                    "display": "fullscreen",
                    "animationIn": "fadeIn",
                    "animationOut": "fadeOut",
                }

                print(f"\n  Generated image item:")
                print(f"    ID:      {new_item['id']}")
                print(f"    Range:   {img_start:.0f}s - {img_end:.0f}s (fullscreen)")
                print(f"    Prompt:  {new_item['imagePrompt']}")

                confirm = input("\n  Add this image? (y/n): ").strip().lower()
                if confirm in ("y", "yes", "si", "s"):
                    items.append(new_item)
                    # Auto-fix overlaps (remove conflicting titles)
                    items = auto_fix_overlaps(items)
                    items.sort(key=lambda i: i["start"])
                    print(f"  [ok] Added {new_item['id']}")
                else:
                    print("  Skipped.")

            except ValueError:
                print("  Usage: add-image <start_seconds> <end_seconds> [fullscreen|pip]")

        elif action == "remove" and len(parts) >= 2:
            target_id = parts[1]
            before = len(items)
            items = [i for i in items if i["id"] != target_id]
            if len(items) < before:
                print(f"  [ok] Removed '{target_id}'")
            else:
                print(f"  Item '{target_id}' not found")

        elif action == "edit-prompt" and len(parts) >= 2:
            target_id = parts[1]
            target = next((i for i in items if i["id"] == target_id and i.get("type") == "image"), None)
            if not target:
                print(f"  Image item '{target_id}' not found")
                continue

            excerpt = get_transcript_in_range(segments, target["start"] - 5, target["end"] + 5)
            display_transcript_range(segments, target["start"], target["end"])
            print("  Describe what you want (or Enter for auto):")
            designer_notes = input("  Notes: ").strip()
            print("  Re-generating imagePrompt with AI...")
            result = generate_image_prompt(client, excerpt, target["start"], target["end"], designer_notes)

            print(f"\n  New prompt: {result.get('imagePrompt', '')}")

            confirm = input("\n  Apply? (y/n): ").strip().lower()
            if confirm in ("y", "yes", "si", "s"):
                target["imagePrompt"] = result.get("imagePrompt", target.get("imagePrompt", ""))
                print(f"  [ok] Updated {target_id}")
            else:
                print("  Skipped.")

        else:
            print("  Commands: show, transcript, add-title, add-image, fill-gaps, fill, edit, remove, edit-prompt, done")

    return items


# ─── Pipeline for a single video ─────────────────────────────────────────────

def process_video(client: Groq, video_path: Path, output_name: str | None = None,
                  force_transcribe: bool = False, duration_override: float | None = None,
                  auto_register: bool = True, interactive: bool = False) -> Path:
    """Run the full pipeline for a single video. Returns the output JSON path."""
    video_src = compute_video_src(video_path)
    stem = video_path.stem
    slug = output_name or slugify(stem)

    print(f"\n{'='*60}")
    print(f"  Pipeline: {video_path.name}")
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

    # Step 3.5: Interactive review (optional)
    if interactive:
        items = interactive_session(client, items, segments, duration)

    # Step 4: Assemble and write JSON
    print("\n[4/5] Assembling JSON...")
    layout_json = assemble_json(video_src, duration, items)

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

def edit_existing_json(client: Groq, json_path: Path):
    """Open an existing layout JSON in interactive editor mode."""
    if not json_path.exists():
        print(f"ERROR: JSON not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        layout = json.load(f)

    items = layout.get("items", [])
    duration = layout["canvas"]["durationInSeconds"]
    video_filename = layout.get("videoSrc", "")

    print(f"\n{'='*60}")
    print(f"  Editing: {json_path.name}")
    print(f"  Video: {video_filename}  |  Duration: {duration}s  |  Items: {len(items)}")
    print(f"{'='*60}")

    # Try to load cached transcript for AI features
    stem = Path(video_filename).stem if video_filename else json_path.stem
    transcript_path = TRANSCRIPTS_DIR / f"{stem}_transcript.json"
    segments = []
    if transcript_path.exists():
        with open(transcript_path, "r", encoding="utf-8") as f:
            segments = json.load(f)
        print(f"  [ok] Transcript loaded: {transcript_path.name} ({len(segments)} segments)")
    else:
        print(f"  [warn] No transcript found at {transcript_path.name}")
        print(f"         AI features (fill-gaps, fill, add-image) will be limited.")
        print(f"         To fix: run the pipeline first with --video to generate the transcript.")

    # Run interactive session
    items = interactive_session(client, items, segments, duration)

    # Save back
    layout["items"] = items
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False, indent=2)
    print(f"\n  [ok] Saved {len(items)} items to {json_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate motion graphics JSON from video files using AI."
    )

    # Input: either a single video, a batch folder, or edit an existing JSON
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--video", help="Path to a single MP4 video file")
    input_group.add_argument("--batch", help="Path to a folder with MP4 videos (processes all)")
    input_group.add_argument("--edit", "-e",
                             help="Edit an existing layout JSON interactively (no re-generation)")

    parser.add_argument("--output", help="Output JSON filename (without extension). Only for --video.")
    parser.add_argument("--force-transcribe", action="store_true",
                        help="Re-transcribe even if cache exists")
    parser.add_argument("--duration", type=float,
                        help="Video duration in seconds (skip ffprobe). Only for --video.")
    parser.add_argument("--no-register", action="store_true",
                        help="Don't auto-register compositions in Root.tsx")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Review items and add/remove images interactively after AI generation")

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

    # ─── Edit mode: open existing JSON directly ───
    if args.edit:
        json_path = Path(args.edit).resolve()
        # If it's just a filename, look in src/data/
        if not json_path.exists() and not json_path.is_absolute():
            json_path = DATA_DIR / args.edit
            if not json_path.suffix:
                json_path = json_path.with_suffix(".json")
        edit_existing_json(client, json_path)
        return

    # Verify ffmpeg is available (only needed for pipeline modes)
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
            interactive=args.interactive,
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
