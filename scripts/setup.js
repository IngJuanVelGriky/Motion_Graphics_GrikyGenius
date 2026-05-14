#!/usr/bin/env node
/**
 * setup.js — Verify all prerequisites for avatar-titles-remotion.
 * Run with: npm run setup
 */

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const ENV_PATH = path.join(__dirname, ".env");
const ENV_EXAMPLE = path.join(__dirname, ".env.example");

let ok = true;

function check(label, fn) {
  try {
    const result = fn();
    console.log(`  [ok] ${label}${result ? ` — ${result}` : ""}`);
  } catch (e) {
    console.log(`  [FAIL] ${label} — ${e.message}`);
    ok = false;
  }
}

console.log("\n  Avatar Titles Remotion — Setup Check\n");

// 1. Node.js version
check("Node.js >= 18", () => {
  const major = parseInt(process.version.slice(1), 10);
  if (major < 18) throw new Error(`Found ${process.version}. Please install Node.js 18 or later.`);
  return process.version;
});

// 2. Python 3
check("Python 3", () => {
  try {
    const ver = execSync("python --version 2>&1", { encoding: "utf-8" }).trim();
    if (!ver.startsWith("Python 3")) throw new Error();
    return ver;
  } catch {
    try {
      const ver = execSync("python3 --version 2>&1", { encoding: "utf-8" }).trim();
      return ver;
    } catch {
      throw new Error(
        "Python 3 not found. Install from https://www.python.org/downloads/"
      );
    }
  }
});

// 3. Python dependencies
check("Python packages (groq, httpx, dotenv)", () => {
  try {
    execSync('python -c "import groq, httpx, dotenv" 2>&1', { encoding: "utf-8" });
    return "installed";
  } catch {
    throw new Error(
      "Missing packages. Run: pip install groq httpx python-dotenv"
    );
  }
});

// 4. ffmpeg
check("ffmpeg", () => {
  try {
    const ver = execSync("ffmpeg -version 2>&1", { encoding: "utf-8" }).split("\n")[0];
    return ver.substring(0, 60);
  } catch {
    throw new Error(
      "ffmpeg not found. Install with:\n" +
      "       Windows: winget install Gyan.FFmpeg\n" +
      "       macOS:   brew install ffmpeg\n" +
      "       Linux:   sudo apt install ffmpeg"
    );
  }
});

// 5. .env file
check("scripts/.env exists with GROQ_API_KEY", () => {
  if (!fs.existsSync(ENV_PATH)) {
    throw new Error(
      `.env not found. Copy the example:\n       cp scripts/.env.example scripts/.env\n       Then add your GROQ_API_KEY (ask the team lead).`
    );
  }
  const content = fs.readFileSync(ENV_PATH, "utf-8");
  if (!content.includes("GROQ_API_KEY=") || content.includes("gsk_your_key_here")) {
    throw new Error(
      "GROQ_API_KEY not configured. Edit scripts/.env and add your key."
    );
  }
  return "configured";
});

// 6. node_modules
check("node_modules installed", () => {
  if (!fs.existsSync(path.join(ROOT, "node_modules"))) {
    throw new Error("Run 'npm install' first.");
  }
  return "present";
});

console.log("");
if (ok) {
  console.log("  All checks passed! You're ready to go.\n");
  console.log("  Quick start:");
  console.log("    1. Place your video in public/ (e.g., public/my-video.mp4)");
  console.log("    2. Run: npm run generate -- --video public/my-video.mp4");
  console.log("    3. Run: npm start  (opens Remotion Studio to preview)");
  console.log("    4. Run: npx remotion render MyVideo out/my-video.mp4\n");
} else {
  console.log("  Some checks failed. Fix the issues above and run again: npm run setup\n");
  process.exit(1);
}
