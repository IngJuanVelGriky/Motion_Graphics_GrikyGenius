# Avatar Titles Remotion

Generates animated title overlays for educational videos using AI. Place a video, run the pipeline, get a finished MP4 with motion graphics highlights.

**Pipeline**: Video → ffmpeg → Groq Whisper → Groq LLM → JSON → Remotion → MP4

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Node.js | >= 18 | [nodejs.org](https://nodejs.org/) |
| Python | >= 3.9 | [python.org](https://www.python.org/downloads/) |
| ffmpeg | any recent | `winget install Gyan.FFmpeg` / `brew install ffmpeg` |
| Groq API key | — | [console.groq.com/keys](https://console.groq.com/keys) or ask team lead |

Python packages: `pip install groq httpx python-dotenv`

---

## Setup (3 steps)

```bash
# 1. Clone and install
git clone <repo-url>
cd avatar-titles-remotion
npm install

# 2. Configure API key
cp scripts/.env.example scripts/.env
# Edit scripts/.env and add your GROQ_API_KEY

# 3. Verify everything works
npm run setup
```

---

## Quick Start

### 1. Place your video
Copy your .mp4 to the `public/` folder.

### 2. Generate highlights
```bash
npm run generate -- --video public/my-video.mp4
```

### 3. Preview
```bash
npm start
```
Opens Remotion Studio at http://localhost:3000. Select your composition from the sidebar.

### 4. Edit (optional)
Open the generated JSON in `src/data/` and tweak titles, timing, or icons. Remotion hot-reloads.

### 5. Render
```bash
npx remotion render MyVideo out/my-video.mp4
```

---

## Using with Claude Desktop / Cowork

This project is designed to work with Claude as your copilot:

1. Open the project in Claude Desktop (or share via Cowork)
2. Claude reads `CLAUDE.md` and knows the full workflow
3. Ask Claude: *"Generate motion graphics for my-video.mp4"*
4. Claude runs the pipeline, helps you edit highlights, and renders the final video

Claude knows the icon catalog, JSON schema, and all project conventions.

---

## Batch Processing

Process all videos in a folder:
```bash
npm run generate -- --batch public/
```

---

## Transparent Export (Alpha Channel)

For compositing in Premiere, DaVinci, or After Effects:

1. Set `SHOW_PREVIEW_BACKGROUND = false` in `src/AvatarSideTitles.tsx`
2. Render: `npx remotion render MyVideo out/video.webm --codec=vp8 --pixel-format=yuva420p`

---

## Project Structure

```
public/              ← Your .mp4 video files
src/data/            ← JSON layout files (one per video)
src/Root.tsx         ← Composition registry (auto-managed)
src/AvatarSideTitles.tsx ← Main Remotion component
scripts/             ← AI pipeline (Python)
transcripts/         ← Cached audio & transcripts
out/                 ← Rendered videos
```

See `CLAUDE.md` for the complete technical reference, JSON schema, and icon catalog.
