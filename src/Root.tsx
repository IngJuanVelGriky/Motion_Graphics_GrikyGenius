import React from "react";
import { Composition } from "remotion";
import { AvatarSideTitles } from "./AvatarSideTitles";
import sampleData from "./data/sample-video-layout.json";
import avatarIvVideo2Data from "./data/avatar-iv-video-2.json";
import t1u1pruebaimagenesData from "./data/t1u1pruebaimagenes.json";
import UIT2Data from "./data/UIT2.json";
import t3Data from "./data/t3.json";
import type { VideoLayout } from "./lib/layout";

const TypedComposition = Composition as React.FC<{
  id: string;
  component: React.FC<VideoLayout>;
  width: number;
  height: number;
  fps: number;
  durationInFrames: number;
  defaultProps: VideoLayout;
}>;

export const RemotionRoot: React.FC = () => {
  const sample = sampleData as VideoLayout;
  const avatarIvVideo2 = avatarIvVideo2Data as VideoLayout;
  const t1u1pruebaimagenes = t1u1pruebaimagenesData as VideoLayout;
  const UIT2 = UIT2Data as VideoLayout;
  const t3 = t3Data as VideoLayout;

  return (
    <>
      <TypedComposition
        id="T3"
        component={AvatarSideTitles}
        width={t3.canvas.width}
        height={t3.canvas.height}
        fps={t3.canvas.fps}
        durationInFrames={t3.canvas.durationInSeconds * t3.canvas.fps}
        defaultProps={t3}
      />
      <TypedComposition
        id="Uit2"
        component={AvatarSideTitles}
        width={UIT2.canvas.width}
        height={UIT2.canvas.height}
        fps={UIT2.canvas.fps}
        durationInFrames={UIT2.canvas.durationInSeconds * UIT2.canvas.fps}
        defaultProps={UIT2}
      />
      <TypedComposition
        id="T1u1pruebaimagenes"
        component={AvatarSideTitles}
        width={t1u1pruebaimagenes.canvas.width}
        height={t1u1pruebaimagenes.canvas.height}
        fps={t1u1pruebaimagenes.canvas.fps}
        durationInFrames={t1u1pruebaimagenes.canvas.durationInSeconds * t1u1pruebaimagenes.canvas.fps}
        defaultProps={t1u1pruebaimagenes}
      />
      <TypedComposition
        id="AvatarSideTitlesDemo"
        component={AvatarSideTitles}
        width={sample.canvas.width}
        height={sample.canvas.height}
        fps={sample.canvas.fps}
        durationInFrames={sample.canvas.durationInSeconds * sample.canvas.fps}
        defaultProps={sample}
      />
      <TypedComposition
        id="AvatarIvVideo2"
        component={AvatarSideTitles}
        width={avatarIvVideo2.canvas.width}
        height={avatarIvVideo2.canvas.height}
        fps={avatarIvVideo2.canvas.fps}
        durationInFrames={avatarIvVideo2.canvas.durationInSeconds * avatarIvVideo2.canvas.fps}
        defaultProps={avatarIvVideo2}
      />
    </>
  );
};
