import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, staticFile } from "remotion";
import { loadFont } from "@remotion/google-fonts/Roboto";
import { TitleBlock } from "./components/TitleBlock";
import {
  secondsToFrames,
  getColumnBox,
  type VideoLayout,
} from "./lib/layout";

const { fontFamily } = loadFont();

// ─── Preview background ───────────────────────────────────────────────────────
// Set to false before exporting with alpha (transparent) channel.
// When true, shows a neutral dark background for in-studio preview.
const SHOW_PREVIEW_BACKGROUND = true;

export const AvatarSideTitles: React.FC<VideoLayout> = ({
  videoSrc,
  canvas,
  layout,
  items,
}) => {
  const { fps } = canvas;

  return (
    <AbsoluteFill>
      {/* ── Preview background (disable for alpha export) ───────────────── */}
      {SHOW_PREVIEW_BACKGROUND && (
        <AbsoluteFill
          style={{ backgroundColor: "#1a1a2e" }}
        />
      )}

      {/* ── Avatar video ────────────────────────────────────────────────── */}
      {videoSrc ? (
        <AbsoluteFill>
          <OffthreadVideo src={staticFile(videoSrc)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </AbsoluteFill>
      ) : (
        /* Placeholder shown when public/avatar.mp4 is not present */
        <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
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
              Coloca tu vídeo en{"\n"}public/avatar.mp4
            </p>
          </div>
        </AbsoluteFill>
      )}

      {/* ── Title overlays ──────────────────────────────────────────────── */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        {items.map((item) => {
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
