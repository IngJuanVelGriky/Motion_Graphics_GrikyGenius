import React from "react";
import {
  AbsoluteFill,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Roboto";
import { TitleBlock } from "./components/TitleBlock";
import { ImageBlock } from "./components/ImageBlock";
import { ClipBlock } from "./components/ClipBlock";
import {
  secondsToFrames,
  getColumnBox,
  isImageItem,
  isClipItem,
  isTitleItem,
  isFullscreenOverlay,
  validateNoOverlap,
  type ClipItem,
  type ImageItem,
  type TitleItem,
  type VideoLayout,
} from "./lib/layout";

const { fontFamily } = loadFont();

// ─── Preview background ───────────────────────────────────────────────────────
const SHOW_PREVIEW_BACKGROUND = true;

// ─── PiP avatar sub-component ────────────────────────────────────────────────

/** A fullscreen overlay item (image or clip) for avatar fade logic. */
type FullscreenOverlayItem = { start: number; end: number; display: string };

const AvatarWithPiP: React.FC<{
  videoSrc: string;
  imageItems: ImageItem[];
  fullscreenOverlays: FullscreenOverlayItem[];
  fps: number;
  canvasWidth: number;
  canvasHeight: number;
}> = ({ videoSrc, imageItems, fullscreenOverlays, fps, canvasWidth, canvasHeight }) => {
  const frame = useCurrentFrame();
  const { fps: configFps } = useVideoConfig();

  const TRANSITION_FRAMES = 18; // ~0.6s smooth crossfade

  // Check if current frame is near any fullscreen overlay (image or clip)
  const activeFullscreen = fullscreenOverlays.find((item) => {
    const itemStart = secondsToFrames(item.start, fps);
    const itemEnd = secondsToFrames(item.end, fps);
    return frame >= itemStart - TRANSITION_FRAMES && frame < itemEnd + TRANSITION_FRAMES;
  });

  // Also check for PiP images specifically
  const activePipImage = imageItems.find((img) => {
    if (img.display !== "pip") return false;
    const imgStart = secondsToFrames(img.start, fps);
    const imgEnd = secondsToFrames(img.end, fps);
    return frame >= imgStart - TRANSITION_FRAMES && frame < imgEnd + TRANSITION_FRAMES;
  });

  // Fullscreen overlay active → fade avatar out, then back in
  if (activeFullscreen) {
    const fsStart = secondsToFrames(activeFullscreen.start, fps);
    const fsEnd = secondsToFrames(activeFullscreen.end, fps);

    const avatarOpacity = (() => {
      if (frame < fsStart) {
        return interpolate(frame, [fsStart - TRANSITION_FRAMES, fsStart], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
      }
      if (frame >= fsEnd) {
        return interpolate(frame, [fsEnd, fsEnd + TRANSITION_FRAMES], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
      }
      return 0;
    })();

    // Never return null — keep video mounted so audio continues playing
    return (
      <div style={{ width: "100%", height: "100%" }}>
        <div style={{ opacity: avatarOpacity, width: "100%", height: "100%" }}>
          <OffthreadVideo
            src={staticFile(videoSrc)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </div>
      </div>
    );
  }

  if (!activePipImage) {
    // Normal full-size avatar
    return (
      <OffthreadVideo
        src={staticFile(videoSrc)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    );
  }

  // PiP mode: shrink avatar to bottom-right corner
  const pipStart = secondsToFrames(activePipImage.start, fps);
  const pipEnd = secondsToFrames(activePipImage.end, fps);

  const scaleIn = spring({
    frame: frame - pipStart,
    fps: configFps,
    config: { damping: 15, stiffness: 120 },
  });

  const scaleOut = spring({
    frame: frame - (pipEnd - 15),
    fps: configFps,
    config: { damping: 15, stiffness: 120 },
  });

  const isExiting = frame >= pipEnd - 15;
  const scale = isExiting ? 0.3 * (1 - scaleOut) + 1 * scaleOut : 1 * (1 - scaleIn) + 0.3 * scaleIn;

  const pipWidth = canvasWidth * scale;
  const pipHeight = canvasHeight * scale;

  const isPip = scale < 0.8;
  const left = isPip ? canvasWidth - pipWidth - 24 : (canvasWidth - pipWidth) / 2;
  const top = isPip ? canvasHeight - pipHeight - 24 : (canvasHeight - pipHeight) / 2;

  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width: pipWidth,
        height: pipHeight,
        borderRadius: isPip ? 16 : 0,
        overflow: "hidden",
        boxShadow: isPip ? "0 8px 32px rgba(0,0,0,0.6)" : "none",
        zIndex: 10,
      }}
    >
      <OffthreadVideo
        src={staticFile(videoSrc)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    </div>
  );
};

// ─── Main composition ────────────────────────────────────────────────────────

export const AvatarSideTitles: React.FC<VideoLayout> = ({
  videoSrc,
  canvas,
  layout,
  items,
}) => {
  const { fps, width: canvasWidth, height: canvasHeight } = canvas;

  // Separate items by type
  const titleItems = items.filter(isTitleItem) as TitleItem[];
  const imageItems = items.filter(isImageItem) as ImageItem[];
  const clipItems = items.filter(isClipItem) as ClipItem[];

  // Combined fullscreen overlays for avatar fade logic
  const fullscreenOverlays = [
    ...imageItems.filter((i) => i.display === "fullscreen"),
    ...clipItems,
  ];

  // Dev-mode overlap warning
  if (process.env.NODE_ENV === "development") {
    const errors = validateNoOverlap(items);
    if (errors.length > 0) {
      console.warn("[AvatarSideTitles] Overlap detected:", errors);
    }
  }

  return (
    <AbsoluteFill>
      {/* ── 1. Preview background (disable for alpha export) ──────────── */}
      {SHOW_PREVIEW_BACKGROUND && (
        <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }} />
      )}

      {/* ── 2. Image overlays (below avatar) ─────────────────────────── */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        {imageItems.map((item) => {
          const startFrame = secondsToFrames(item.start, fps);
          const endFrame = secondsToFrames(item.end, fps);
          const durationInFrames = endFrame - startFrame;

          return (
            <Sequence
              key={item.id}
              from={startFrame}
              durationInFrames={durationInFrames}
            >
              <ImageBlock
                item={item}
                canvasWidth={canvasWidth}
                canvasHeight={canvasHeight}
                durationInFrames={durationInFrames}
              />
            </Sequence>
          );
        })}
      </AbsoluteFill>

      {/* ── 2b. Clip overlays (below avatar, same layer as images) ──── */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        {clipItems.map((item) => {
          const startFrame = secondsToFrames(item.start, fps);
          const endFrame = secondsToFrames(item.end, fps);
          const durationInFrames = endFrame - startFrame;

          return (
            <Sequence
              key={item.id}
              from={startFrame}
              durationInFrames={durationInFrames}
            >
              <ClipBlock
                item={item}
                canvasWidth={canvasWidth}
                canvasHeight={canvasHeight}
                durationInFrames={durationInFrames}
              />
            </Sequence>
          );
        })}
      </AbsoluteFill>

      {/* ── 3. Avatar video (with PiP support) ───────────────────────── */}
      {videoSrc ? (
        <AbsoluteFill>
          <AvatarWithPiP
            videoSrc={videoSrc}
            imageItems={imageItems}
            fullscreenOverlays={fullscreenOverlays}
            fps={fps}
            canvasWidth={canvasWidth}
            canvasHeight={canvasHeight}
          />
        </AbsoluteFill>
      ) : (
        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              position: "absolute",
              left: layout.center.x,
              top: layout.center.y,
              width: layout.center.width,
              height: layout.center.height,
              background: "rgba(255,255,255,0.05)",
              border: "2px dashed rgba(255,255,255,0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <p
              style={{
                color: "rgba(255,255,255,0.4)",
                fontFamily: "'Helvetica Neue', Arial, sans-serif",
                fontSize: 24,
                textAlign: "center",
              }}
            >
              Coloca tu video en{"\n"}public/avatar.mp4
            </p>
          </div>
        </AbsoluteFill>
      )}

      {/* ── 4. Title overlays (on top of everything) ──────────────────── */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        {titleItems.map((item) => {
          const startFrame = secondsToFrames(item.start, fps);
          const endFrame = secondsToFrames(item.end, fps);
          const durationInFrames = endFrame - startFrame;
          const box = getColumnBox(item.column, layout);

          return (
            <Sequence
              key={item.id}
              from={startFrame}
              durationInFrames={durationInFrames}
            >
              <TitleBlock
                item={item}
                box={box}
                durationInFrames={durationInFrames}
                fontFamily={fontFamily}
              />
            </Sequence>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
