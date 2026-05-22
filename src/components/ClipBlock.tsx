import React from "react";
import { OffthreadVideo, interpolate, staticFile, useCurrentFrame } from "remotion";
import type { CSSProperties } from "react";
import type { ClipItem } from "../lib/layout";
import { FiFilm } from "react-icons/fi";

interface ClipBlockProps {
  item: ClipItem;
  canvasWidth: number;
  canvasHeight: number;
  durationInFrames: number;
}

const ANIM_IN_FRAMES = 15;
const ANIM_OUT_FRAMES = 12;

export const ClipBlock: React.FC<ClipBlockProps> = ({
  item,
  canvasWidth,
  canvasHeight,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();

  const inProgress = interpolate(frame, [0, ANIM_IN_FRAMES], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const outStart = durationInFrames - ANIM_OUT_FRAMES;
  const outProgress = interpolate(frame, [outStart, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const opacity = inProgress * (1 - outProgress);

  if (item.src === "NEEDS_CLIP") {
    return (
      <ClipPlaceholder
        item={item}
        opacity={opacity}
        canvasWidth={canvasWidth}
        canvasHeight={canvasHeight}
      />
    );
  }

  return (
    <FullscreenClip
      item={item}
      opacity={opacity}
      canvasWidth={canvasWidth}
      canvasHeight={canvasHeight}
    />
  );
};

// ─── Fullscreen clip ────────────────────────────────────────────────────────

const FullscreenClip: React.FC<{
  item: ClipItem;
  opacity: number;
  canvasWidth: number;
  canvasHeight: number;
}> = ({ item, opacity, canvasWidth, canvasHeight }) => {
  const containerStyle: CSSProperties = {
    position: "absolute",
    left: 0,
    top: 0,
    width: canvasWidth,
    height: canvasHeight,
    backgroundColor: "#0a0a0a",
    opacity,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
  };

  const videoStyle: CSSProperties = {
    width: "100%",
    height: item.caption ? "85%" : "100%",
    objectFit: "contain",
  };

  const captionStyle: CSSProperties = {
    color: "#FFFFFF",
    fontSize: 28,
    fontFamily: "'Roboto', sans-serif",
    fontWeight: 500,
    textAlign: "center",
    padding: "16px 40px",
    textShadow: "0 2px 12px rgba(0,0,0,0.6)",
  };

  return (
    <div style={containerStyle}>
      <OffthreadVideo src={staticFile(item.src)} muted style={videoStyle} />
      {item.caption && <p style={captionStyle}>{item.caption}</p>}
    </div>
  );
};

// ─── Placeholder (NEEDS_CLIP) ───────────────────────────────────────────────

const ClipPlaceholder: React.FC<{
  item: ClipItem;
  opacity: number;
  canvasWidth: number;
  canvasHeight: number;
}> = ({ item, opacity, canvasWidth, canvasHeight }) => {
  const containerStyle: CSSProperties = {
    position: "absolute",
    left: 0,
    top: 0,
    width: canvasWidth,
    height: canvasHeight,
    opacity,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  };

  const boxStyle: CSSProperties = {
    width: canvasWidth * 0.6,
    height: canvasHeight * 0.5,
    border: "3px dashed rgba(255,255,255,0.4)",
    borderRadius: 20,
    background: "rgba(0,0,0,0.3)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: 20,
    padding: 40,
  };

  const labelStyle: CSSProperties = {
    color: "rgba(255,255,255,0.5)",
    fontSize: 18,
    fontFamily: "'Roboto', sans-serif",
    fontWeight: 500,
    textTransform: "uppercase",
    letterSpacing: "0.1em",
  };

  const promptStyle: CSSProperties = {
    color: "rgba(255,255,255,0.7)",
    fontSize: 22,
    fontFamily: "'Roboto', sans-serif",
    fontWeight: 400,
    textAlign: "center",
    lineHeight: 1.5,
    maxWidth: "90%",
  };

  return (
    <div style={containerStyle}>
      <div style={boxStyle}>
        <FiFilm size={64} color="rgba(255,255,255,0.35)" />
        <p style={labelStyle}>Clip Placeholder</p>
        {item.clipPrompt && <p style={promptStyle}>{item.clipPrompt}</p>}
      </div>
    </div>
  );
};
