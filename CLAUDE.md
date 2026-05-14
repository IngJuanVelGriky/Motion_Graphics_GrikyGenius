# Avatar Titles Remotion — Motion Graphics Generator

## What this project does
Generates animated title overlays for educational videos with an avatar speaker.
A JSON file defines when and where titles appear; Remotion renders the final MP4.

The pipeline: **Video → Audio → Transcript → AI Highlights → JSON → Remotion → MP4**

## Project structure
```
avatar-titles-remotion/
├── public/              ← Place your .mp4 videos here
├── src/
│   ├── Root.tsx          ← Registers Remotion compositions
│   ├── AvatarSideTitles.tsx ← Main composition component
│   ├── components/
│   │   └── TitleBlock.tsx    ← Animated title with icon
│   ├── data/
│   │   └── *.json            ← Layout JSONs (one per video)
│   └── lib/
│       ├── layout.ts         ← Types and helpers
│       └── icons.ts          ← 287 Feather icons mapped by name
├── scripts/
│   ├── generate_layout.py    ← AI pipeline (ffmpeg → Groq Whisper → Groq LLM → JSON)
│   ├── prompt_template.txt   ← LLM prompt for highlight generation
│   ├── .env                  ← Your GROQ_API_KEY (not in Git)
│   └── .env.example
├── transcripts/         ← Cached audio/transcript files (not in Git)
├── out/                 ← Rendered videos (not in Git)
└── examples/            ← Example outputs (not in Git)
```

---

## Workflow: Generating motion graphics for a new video

When the user asks to generate highlights / motion graphics for a video, follow these steps:

### Step 1 — Place the video
The user should place their .mp4 file in `public/`. Example: `public/my-video.mp4`

### Step 2 — Run the AI pipeline
```bash
cd scripts
python generate_layout.py --video ../public/my-video.mp4
```

This will:
1. Extract audio with ffmpeg
2. Transcribe with Groq Whisper
3. Generate editorial highlights with Groq LLM
4. Write a JSON to `src/data/<slug>.json`
5. Auto-register the composition in `src/Root.tsx`

### Step 3 — Preview in Remotion Studio
```bash
npm start
```
Opens http://localhost:3000. Select the new composition from the sidebar.

### Step 4 — Edit the highlights (optional)
The user can ask to modify the JSON. Edit the file in `src/data/`. Remotion hot-reloads.

Common edits:
- Change text: edit `"text"` field
- Move timing: adjust `"start"` / `"end"` (in seconds)
- Change icon: update `"icon"` field (see icon catalog below)
- Change position: set `"column"` to `"left"` or `"right"`
- Change size: use `"variant": "headline"` (large) or `"subheadline"` (smaller)

### Step 5 — Render the final video
```bash
npx remotion render <CompositionId> out/<filename>.mp4
```
Example: `npx remotion render MyVideo out/my-video.mp4`

For transparent output (alpha channel, for compositing):
```bash
npx remotion render <CompositionId> out/video.webm --codec=vp8 --pixel-format=yuva420p
```

---

## JSON Schema Reference

Each layout JSON has this structure:

```json
{
  "videoSrc": "my-video.mp4",
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
  "items": [
    {
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
  ]
}
```

### Item rules
- `column`: `"left"` or `"right"` — titles alternate sides
- `animationIn`: use `"slideRightFade"` for left column, `"slideLeftFade"` for right
- `animationOut`: always `"fadeOut"`
- `variant`: `"headline"` (64px bold) or `"subheadline"` (36px medium)
- `verticalAlign`: `"top"`, `"center"`, or `"bottom"`
- `fontSize`: optional override (number in pixels)
- Items should be visible 4-5 seconds each with 2+ second gaps

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

- **Relative paths only**: The `videoSrc` field in JSON should be just the filename (e.g., `"my-video.mp4"`), not an absolute path. The file must exist in `public/`.
- **Never hardcode absolute paths** in any configuration or JSON.
- **Root.tsx auto-registration**: The `generate_layout.py` script auto-adds compositions to `Root.tsx`. If manually adding, follow the pattern in the existing file.
- **Font**: The project uses Google Font "Roboto" loaded via `@remotion/google-fonts`.
- **Canvas**: Standard is 1920x1080 at 30fps.
- **Transcripts are cached**: Audio and transcripts are cached in `transcripts/`. Use `--force-transcribe` to regenerate.

---

## Troubleshooting

### "Cannot find module" error after generating
The `generate_layout.py` script should auto-register in `Root.tsx`. If it didn't, manually add:
1. An import for the JSON file
2. A cast to `VideoLayout`
3. A `<TypedComposition>` block

### ffmpeg not found
Install with `winget install Gyan.FFmpeg` (Windows) or `brew install ffmpeg` (macOS).

### Groq API errors
- Check `scripts/.env` has a valid `GROQ_API_KEY`
- Audio files must be under 25 MB for Whisper
- If SSL errors occur, the script uses `verify=False` on httpx as a workaround

### Video doesn't show in preview
- Ensure the .mp4 is in `public/`, not in `src/`
- Ensure `videoSrc` in the JSON matches the filename exactly (case-sensitive)

### Rendering is slow
- Use `--concurrency=4` or higher: `npx remotion render MyVideo out/v.mp4 --concurrency=4`
- VP8/VP9 transparent renders are slower than MP4

---

## Batch processing
Process all videos in a folder at once:
```bash
cd scripts
python generate_layout.py --batch ../public/
```
This processes every .mp4 in the folder sequentially.
