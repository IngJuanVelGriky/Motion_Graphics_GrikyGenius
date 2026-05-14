import type { CSSProperties } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

export type Column = "left" | "right";
export type VerticalAlign = "top" | "center" | "bottom";
export type Variant = "headline" | "subheadline";
export type AnimationIn = "slideRightFade" | "slideLeftFade" | "fadeIn";
export type AnimationOut = "fadeOut";

export interface ColumnBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface LayoutConfig {
  left: ColumnBox;
  center: ColumnBox;
  right: ColumnBox;
}

export interface TitleItem {
  id: string;
  text: string;
  icon?: string;
  start: number;
  end: number;
  column: Column;
  verticalAlign: VerticalAlign;
  variant: Variant;
  animationIn: AnimationIn;
  animationOut: AnimationOut;
  fontSize?: number;
}

export interface CanvasConfig {
  width: number;
  height: number;
  fps: number;
  durationInSeconds: number;
}

export interface VideoLayout {
  videoSrc: string;
  canvas: CanvasConfig;
  layout: LayoutConfig;
  items: TitleItem[];
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

export function secondsToFrames(seconds: number, fps: number): number {
  return Math.round(seconds * fps);
}

export function getColumnBox(column: Column, layout: LayoutConfig): ColumnBox {
  return layout[column];
}

export function getVerticalPositionStyle(
  verticalAlign: VerticalAlign
): CSSProperties {
  if (verticalAlign === "top") {
    return { top: 0, bottom: "auto" };
  }
  if (verticalAlign === "bottom") {
    return { bottom: 0, top: "auto" };
  }
  // center: use flexbox on the parent container
  return { top: "50%", transform: "translateY(-50%)" };
}

// ─── Variant styles ───────────────────────────────────────────────────────────

export const VARIANT_STYLES: Record<Variant, CSSProperties> = {
  headline: {
    fontSize: 64,
    fontWeight: 800,
    lineHeight: 1.1,
    letterSpacing: "-0.02em",
  },
  subheadline: {
    fontSize: 36,
    fontWeight: 500,
    lineHeight: 1.3,
    letterSpacing: "-0.01em",
  },
};
