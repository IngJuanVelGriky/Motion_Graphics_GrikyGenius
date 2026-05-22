import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import type { CSSProperties } from "react";
import type { ImageItem } from "../lib/layout";
import { FiImage } from "react-icons/fi";

interface ImageBlockProps {
  item: ImageItem;
  canvasWidth: number;
  canvasHeight: number;
  durationInFrames: number;
}

const ANIM_IN_FRAMES = 15;
const ANIM_OUT_FRAMES = 12;

export const ImageBlock: React.FC<ImageBlockProps> = ({
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

  const isPlaceholder = item.src === "NEEDS_IMAGE";

  if (isPlaceholder) {
    return <PlaceholderBlock item={item} opacity={opacity} canvasWidth={canvasWidth} canvasHeight={canvasHeight} />;
  }

  if (item.display === "fullscreen") {
    return <FullscreenImage item={item} opacity={opacity} canvasWidth={canvasWidth} canvasHeight={canvasHeight} />;
  }

  return <PipImage item={item} opacity={opacity} canvasWidth={canvasWidth} canvasHeight={canvasHeight} />;
};

// ─── Fullscreen mode ─────────────────────────────────────────────────────────

const FullscreenImage: React.FC<{
  item: ImageItem;
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

  const imgStyle: CSSProperties = {
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
      <Img src={staticFile(item.src)} style={imgStyle} />
      {item.caption && <p style={captionStyle}>{item.caption}</p>}
    </div>
  );
};

// ─── PiP mode ────────────────────────────────────────────────────────────────

const PipImage: React.FC<{
  item: ImageItem;
  opacity: number;
  canvasWidth: number;
  canvasHeight: number;
}> = ({ item, opacity, canvasWidth, canvasHeight }) => {
  const padding = 60;
  const containerStyle: CSSProperties = {
    position: "absolute",
    left: padding,
    top: padding,
    width: canvasWidth - padding * 2,
    height: canvasHeight - padding * 2 - (item.caption ? 60 : 0),
    opacity,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
  };

  const imgStyle: CSSProperties = {
    maxWidth: "100%",
    maxHeight: "100%",
    objectFit: "contain",
    borderRadius: 16,
    boxShadow: "0 8px 40px rgba(0,0,0,0.5)",
  };

  const captionStyle: CSSProperties = {
    color: "#FFFFFF",
    fontSize: 24,
    fontFamily: "'Roboto', sans-serif",
    fontWeight: 400,
    textAlign: "center",
    marginTop: 12,
    textShadow: "0 2px 8px rgba(0,0,0,0.5)",
  };

  return (
    <div style={containerStyle}>
      <Img src={staticFile(item.src)} style={imgStyle} />
      {item.caption && <p style={captionStyle}>{item.caption}</p>}
    </div>
  );
};

// ─── Placeholder (NEEDS_IMAGE) ───────────────────────────────────────────────

const PlaceholderBlock: React.FC<{
  item: ImageItem;
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

  const modeStyle: CSSProperties = {
    color: "rgba(255,255,255,0.35)",
    fontSize: 14,
    fontFamily: "'Roboto', sans-serif",
    fontWeight: 400,
  };

  return (
    <div style={containerStyle}>
      <div style={boxStyle}>
        <FiImage size={64} color="rgba(255,255,255,0.35)" />
        <p style={labelStyle}>Image Placeholder</p>
        {item.imagePrompt && <p style={promptStyle}>{item.imagePrompt}</p>}
        <p style={modeStyle}>Mode: {item.display}</p>
      </div>
    </div>
  );
};
