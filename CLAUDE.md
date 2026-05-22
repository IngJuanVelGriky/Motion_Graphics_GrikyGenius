# Avatar Titles Remotion — Motion Graphics Generator

## What this project does
Generates animated overlay motion graphics (titles, images, and clips) for educational videos with an avatar speaker. A JSON file defines when and where overlays appear; Remotion renders the final MP4.

**Design philosophy**: The avatar is visible only ~30% of the video. The remaining ~70% is covered by fullscreen overlays — images and clips, split roughly 50/50. Titles only appear during avatar-visible moments.

The pipeline: **Video → Audio → Transcript → AI Highlights → JSON → Remotion → MP4**

## Project structure
```
avatar-titles-remotion/
├── public/                    ← Videos and assets, organized by course
│   └── {diplomado}/{curso}/{unidad}/
│       ├── avatar.mp4         ← Main video
│       ├── img1.png           ← Generated images
│       └── clip1.mp4          ← Generated clips
├── src/
│   ├── Root.tsx               ← Registers Remotion compositions
│   ├── AvatarSideTitles.tsx   ← Main composition component
│   ├── components/
│   │   ├── TitleBlock.tsx     ← Animated title with icon
│   │   ├── ImageBlock.tsx     ← Image overlay (fullscreen/PiP/placeholder)
│   │   └── ClipBlock.tsx      ← Clip video overlay (fullscreen/placeholder)
│   ├── data/
│   │   └── *.json             ← Layout JSONs (one per video)
│   └── lib/
│       ├── layout.ts          ← Types and helpers
│       └── icons.ts           ← 287 Feather icons mapped by name
├── scripts/
│   ├── generate_layout.py     ← AI pipeline (ffmpeg → Groq Whisper → Groq LLM → JSON)
│   ├── prompt_template.txt    ← LLM prompt for highlight generation
│   ├── .env                   ← Your GROQ_API_KEY (not in Git)
│   └── .env.example
├── transcripts/               ← Cached audio/transcript files (not in Git)
├── out/                       ← Rendered videos (not in Git)
└── examples/                  ← Example outputs (not in Git)
```

---

## Workflow: Generating motion graphics for a new video

### Step 1 — Place the video
Place the .mp4 in `public/`, ideally in a subfolder structure:
```
public/accclimatica/curso1/u1/avatar.mp4
```
Legacy: `public/my-video.mp4` still works.

### Step 2 — Run the AI pipeline
```bash
cd scripts
python generate_layout.py --video ../public/accclimatica/curso1/u1/avatar.mp4
```

This will:
1. Extract audio with ffmpeg
2. Transcribe with Groq Whisper
3. Generate editorial highlights (titles, images, clips) with Groq LLM
4. Write a JSON to `src/data/<slug>.json`
5. Auto-register the composition in `src/Root.tsx`

### Step 3 — Preview in Remotion Studio
```bash
npm start
```

### Step 4 — Provide assets
- Replace `"NEEDS_IMAGE"` with actual image paths (relative to `public/`)
- Replace `"NEEDS_CLIP"` with actual clip paths (relative to `public/`)
- Generate images from `imagePrompt` using DALL-E/Midjourney
- Generate clips from `clipPrompt` using video generation tools

### Step 5 — Render
```bash
npx remotion render <CompositionId> out/<filename>.mp4
```

---

## JSON Schema Reference

```json
{
  "videoSrc": "accclimatica/curso1/u1/avatar.mp4",
  "canvas": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "durationInSeconds": 120
  },
  "layout": {
    "left":   { "x": 80,   "y": 140, "width": 480, "height": 800 },
    "center": { "x": 640,  "y": 0,   "width": 640, "height": 1080 },
    "right":  { "x": 1360, "y": 140, "width": 480, "height": 800 }
  },
  "items": [ ... ]
}
```

`videoSrc` supports subdirectory paths relative to `public/`.

### Title Item schema
```json
{
  "type": "title",
  "id": "h1",
  "text": "Short punchy title",
  "icon": "FiDatabase",
  "start": 5,
  "end": 9,
  "column": "left",
  "verticalAlign": "center",
  "variant": "headline",
  "animationIn": "slideRightFade",
  "animationOut": "fadeOut"
}
```

### Title Item rules
- `type`: `"title"` (optional, default)
- `column`: `"left"` or `"right"` — titles alternate sides
- `animationIn`: `"slideRightFade"` for left, `"slideLeftFade"` for right
- `animationOut`: always `"fadeOut"`
- `variant`: `"headline"` (64px bold) or `"subheadline"` (36px medium)
- `fontSize`: optional override (pixels)
- Visible 4-5 seconds, 2+ second gaps
- **Titles only appear during avatar-visible time (~30% of video)**

### Image Item schema
```json
{
  "type": "image",
  "id": "img1",
  "src": "NEEDS_IMAGE",
  "caption": "Optional caption",
  "imagePrompt": "2-3 sentence description for AI image generation",
  "start": 25,
  "end": 33,
  "display": "fullscreen",
  "animationIn": "fadeIn",
  "animationOut": "fadeOut"
}
```

### Image Item rules
- `type`: `"image"` (REQUIRED)
- `display`: `"fullscreen"` (covers canvas, avatar hidden) or `"pip"` (avatar shrinks to corner)
- `src`: `"NEEDS_IMAGE"` for placeholders; replace with path relative to `public/`
- `imagePrompt`: AI image generation prompt. **Must follow the Visual Style Guide.**
- Visible 5-10 seconds each
- **No title may overlap with an image's time range** (2s buffer)

### Clip Item schema
```json
{
  "type": "clip",
  "id": "clip1",
  "src": "NEEDS_CLIP",
  "clipPrompt": "Contextual description of the ideal clip, in the same language as the transcript",
  "caption": "Optional caption",
  "start": 40,
  "end": 48,
  "display": "fullscreen",
  "animationIn": "fadeIn",
  "animationOut": "fadeOut"
}
```

### Clip Item rules
- `type`: `"clip"` (REQUIRED)
- `display`: always `"fullscreen"` — clips cover the entire canvas, avatar is hidden
- `src`: `"NEEDS_CLIP"` for placeholders; replace with .mp4 path relative to `public/`
- `clipPrompt`: 2-3 sentences describing the ideal clip, in the same language as the transcript
- Clips are always rendered **muted** — the avatar's audio continues playing
- Visible 5-10 seconds each
- **No title or other fullscreen item may overlap** (2s buffer)
- Style: warm corporate aesthetic coherent with the project's visual identity

---

## Design Philosophy — Overlay Distribution

| Element | Screen time | Notes |
|---------|-------------|-------|
| Avatar visible | ~30% | Speaker is on screen |
| Images (fullscreen) | ~35% | Static visuals, infographics, data |
| Clips (fullscreen) | ~35% | Motion video overlays |
| Titles | During avatar time only | Text + icon overlays |

The AI pipeline automatically distributes overlays to achieve this balance.

---

## Visual Style Guide for Image Prompts

### Mandatory style suffix for every imagePrompt
- Dark warm background (#1a1a2e to #2d1b00 gradient), amber/golden accents, soft warm glow
- Premium corporate infographic, cinematic quality, NO white backgrounds, NO clip-art
- Sans-serif typography, warm palette: amber (#F59E0B), gold (#D4A574), warm white (#FFF8F0), teal (#5EEAD4) accent

### Text minimization
- Viewer has 5-10 seconds — image must be understood at a glance
- Prefer visual elements over text labels
- When data is essential, show numbers LARGE with single-word labels

### What to avoid
- White/light backgrounds, flat clip-art, bright primary colors, dense diagrams

### What works well
- Dark warm infographics with amber/gold highlights
- Iconographic representations, charts with warm gradients
- Visual metaphors (glowing pyramid > text list)

---

## Icon Catalog

All icons use the Feather icon set from `react-icons/fi`. Use the exact string name in the JSON.

### Data & Analytics
FiDatabase, FiBarChart, FiBarChart2, FiPieChart, FiTrendingUp, FiTrendingDown, FiActivity, FiPercent, FiHash, FiTable

### Technology & Code
FiCode, FiTerminal, FiCpu, FiServer, FiHardDrive, FiCloud, FiCloudOff, FiCloudLightning, FiWifi, FiWifiOff, FiBluetooth, FiMonitor, FiSmartphone, FiTablet, FiTv, FiAirplay, FiGitBranch, FiGitCommit, FiGitMerge, FiGitPullRequest, FiCodesandbox, FiCodepen, FiCommand

### Communication
FiMail, FiInbox, FiSend, FiMessageCircle, FiMessageSquare, FiPhone, FiPhoneCall, FiPhoneIncoming, FiPhoneOutgoing, FiMic, FiMicOff, FiVideo, FiVideoOff, FiVoicemail, FiRadio, FiRss, FiAtSign

### Media & Content
FiPlay, FiPlayCircle, FiPause, FiPauseCircle, FiStopCircle, FiSkipBack, FiSkipForward, FiFastForward, FiRewind, FiVolume, FiVolume1, FiVolume2, FiVolumeX, FiMusic, FiHeadphones, FiSpeaker, FiFilm, FiCamera, FiImage, FiDisc, FiCast, FiYoutube

### Files & Documents
FiFile, FiFileText, FiFilePlus, FiFileMinus, FiFolder, FiFolderPlus, FiFolderMinus, FiClipboard, FiArchive, FiBook, FiBookOpen, FiBookmark, FiPaperclip, FiPrinter, FiSave, FiDownload, FiUpload, FiDownloadCloud, FiUploadCloud, FiCopy

### Security & Access
FiLock, FiUnlock, FiKey, FiShield, FiShieldOff, FiEye, FiEyeOff, FiLogIn, FiLogOut, FiUserCheck, FiUserX

### People & Social
FiUser, FiUsers, FiUserPlus, FiUserMinus, FiSmile, FiFrown, FiMeh, FiHeart, FiThumbsUp, FiThumbsDown, FiShare, FiShare2, FiLinkedin, FiFacebook, FiTwitter, FiInstagram

### Status & Feedback
FiCheck, FiCheckCircle, FiCheckSquare, FiX, FiXCircle, FiXOctagon, FiXSquare, FiAlertCircle, FiAlertTriangle, FiAlertOctagon, FiInfo, FiHelpCircle, FiBell, FiBellOff

### Navigation & Direction
FiArrowUp, FiArrowDown, FiArrowLeft, FiArrowRight, FiArrowUpRight, FiArrowUpLeft, FiArrowDownRight, FiArrowDownLeft, FiChevronUp, FiChevronDown, FiChevronLeft, FiChevronRight, FiCornerUpRight, FiCornerDownRight, FiCompass, FiNavigation, FiNavigation2, FiMap, FiMapPin, FiExternalLink, FiLink, FiLink2, FiHome, FiGlobe, FiTarget, FiCrosshair

### Business & Finance
FiBriefcase, FiDollarSign, FiCreditCard, FiShoppingCart, FiShoppingBag, FiPackage, FiTruck, FiGift, FiAward, FiStar, FiFlag, FiTag

### Tools & Settings
FiSettings, FiTool, FiSliders, FiFilter, FiEdit, FiEdit2, FiEdit3, FiPenTool, FiScissors, FiCrop, FiSearch, FiZoomIn, FiZoomOut, FiRefreshCw, FiRefreshCcw, FiRotateCw, FiRotateCcw, FiRepeat, FiShuffle, FiMove, FiTrash, FiTrash2, FiDelete, FiPlus, FiPlusCircle, FiMinus, FiMinusCircle, FiMaximize, FiMinimize, FiToggleLeft, FiToggleRight, FiPower

### Layout & Design
FiLayout, FiLayers, FiGrid, FiColumns, FiSidebar, FiSquare, FiCircle, FiTriangle, FiHexagon, FiOctagon, FiBox, FiFeather, FiFigma, FiFramer, FiAlignLeft, FiAlignCenter, FiAlignRight, FiAlignJustify, FiBold, FiItalic, FiUnderline, FiType, FiList, FiMenu, FiMoreHorizontal, FiMoreVertical

### Time & Energy
FiClock, FiWatch, FiCalendar, FiZap, FiZapOff, FiBattery, FiBatteryCharging, FiSun, FiSunrise, FiSunset, FiMoon, FiLoader

### Nature & Misc
FiDroplet, FiCloudRain, FiCloudSnow, FiCloudDrizzle, FiWind, FiUmbrella, FiThermometer, FiAperture, FiAnchor, FiLifeBuoy, FiSlash, FiDivide, FiMousePointer, FiPocket

---

## Important rules

- **Relative paths**: `videoSrc` and item `src` fields use paths relative to `public/` (e.g., `"accclimatica/curso1/u1/avatar.mp4"`). Legacy plain filenames still work.
- **Never hardcode absolute paths** in any configuration or JSON.
- **Root.tsx auto-registration**: The `generate_layout.py` script auto-adds compositions to `Root.tsx`.
- **Font**: Google Font "Roboto" via `@remotion/google-fonts`.
- **Canvas**: 1920x1080 at 30fps.
- **Transcripts are cached**: Use `--force-transcribe` to regenerate.

---

## Troubleshooting

### "Cannot find module" error after generating
Manually add to Root.tsx: import, cast to VideoLayout, TypedComposition block.

### ffmpeg not found
`winget install Gyan.FFmpeg` (Windows) or `brew install ffmpeg` (macOS).

### Groq API errors
- Check `scripts/.env` has a valid `GROQ_API_KEY`
- Audio files must be under 25 MB
- SSL errors: script uses `verify=False` on httpx

### Video/clip doesn't show in preview
- Ensure files are in `public/` (or subdirectory)
- Ensure paths in JSON match exactly (case-sensitive, forward slashes)

### Rendering is slow
- `--concurrency=4`: `npx remotion render MyVideo out/v.mp4 --concurrency=4`

---

## Batch processing
```bash
cd scripts
python generate_layout.py --batch ../public/accclimatica/curso1/
```
