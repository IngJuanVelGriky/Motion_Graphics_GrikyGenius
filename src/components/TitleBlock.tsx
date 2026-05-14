import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import type { CSSProperties } from "react";
import {
  getVerticalPositionStyle,
  VARIANT_STYLES,
  type ColumnBox,
  type TitleItem,
} from "../lib/layout";
import { getIcon } from "../lib/icons";

interface TitleBlockProps {
  item: TitleItem;
  box: ColumnBox;
  durationInFrames: number;
  fontFamily: string;
}

const ANIM_IN_FRAMES = 18;
const ANIM_OUT_FRAMES = 12;
const SLIDE_DISTANCE = 48;

const ICON_SIZE: Record<TitleItem["variant"], number> = {
  headline: 140,
  subheadline: 90,
};

export const TitleBlock: React.FC<TitleBlockProps> = ({
  item,
  box,
  durationInFrames,
  fontFamily,
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

  let translateX = 0;
  if (item.animationIn === "slideRightFade") {
    translateX = interpolate(inProgress, [0, 1], [-SLIDE_DISTANCE, 0]);
  } else if (item.animationIn === "slideLeftFade") {
    translateX = interpolate(inProgress, [0, 1], [SLIDE_DISTANCE, 0]);
  }

  const verticalStyle = getVerticalPositionStyle(item.verticalAlign);
  const variantStyle = VARIANT_STYLES[item.variant];
  const IconComponent = item.icon ? getIcon(item.icon) : null;
  const iconSize = ICON_SIZE[item.variant];

  const containerStyle: CSSProperties = {
    position: "absolute",
    left: box.x,
    top: box.y,
    width: box.width,
    height: box.height,
    pointerEvents: "none",
  };

  const innerStyle: CSSProperties = {
    position: "absolute",
    width: "100%",
    ...verticalStyle,
  };

  const contentStyle: CSSProperties = {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 16,
    padding: "10px 0",
    opacity,
    transform: `translateX(${translateX}px)`,
  };

  const iconStyle: CSSProperties = {
    color: "#FFFFFF",
    filter: "drop-shadow(0 2px 12px rgba(0,0,0,0.4))",
    flexShrink: 0,
  };

  const textStyle: CSSProperties = {
    ...variantStyle,
    ...(item.fontSize != null ? { fontSize: item.fontSize } : {}),
    fontFamily,
    color: "#FFFFFF",
    margin: 0,
    padding: 0,
    textAlign: "center",
    textShadow: "0 2px 20px rgba(0,0,0,0.45)",
    maxWidth: box.width,
    wordBreak: "keep-all",
    overflowWrap: "break-word",
  };

  return (
    <div style={containerStyle}>
      <div style={innerStyle}>
        <div style={contentStyle}>
          {IconComponent && (
            <IconComponent size={iconSize} style={iconStyle} />
          )}
          <p style={textStyle}>{item.text}</p>
        </div>
      </div>
    </div>
  );
};
