import React from "react";
import { Composition } from "remotion";
import { AvatarSideTitles } from "./AvatarSideTitles";
import sampleData from "./data/sample-video-layout.json";
import avatarIvVideo2Data from "./data/avatar-iv-video-2.json";
import t1pruebaData from "./data/t1prueba.json";
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

  const t1prueba = t1pruebaData as VideoLayout;

  return (
    <>
      <TypedComposition
        id="T1prueba"
        component={AvatarSideTitles}
        width={t1prueba.canvas.width}
        height={t1prueba.canvas.height}
        fps={t1prueba.canvas.fps}
        durationInFrames={t1prueba.canvas.durationInSeconds * t1prueba.canvas.fps}
        defaultProps={t1prueba}
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
