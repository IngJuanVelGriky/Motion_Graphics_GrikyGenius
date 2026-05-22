import type { CSSProperties } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

export type Column = "left" | "right";
export type VerticalAlign = "top" | "center" | "bottom";
export type Variant = "headline" | "subheadline";
export type AnimationIn = "slideRightFade" | "slideLeftFade" | "fadeIn";
export type AnimationOut = "fadeOut";
export type ImageDisplay = "fullscreen" | "pip";

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
  type?: "title";
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

export interface ImageItem {
  type: "image";
  id: string;
  src: string;
  caption?: string;
  imagePrompt?: string;
  start: number;
  end: number;
  display: ImageDisplay;
  animationIn: AnimationIn;
  animationOut: AnimationOut;
}

export interface ClipItem {
  type: "clip";
  id: string;
  src: string;
  clipPrompt?: string;
  caption?: string;
  start: number;
  end: number;
  display: "fullscreen";
  animationIn: AnimationIn;
  animationOut: AnimationOut;
}

export type LayoutItem = TitleItem | ImageItem | ClipItem;

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
  items: LayoutItem[];
}

// ─── Type guards ─────────────────────────────────────────────────────────────

export function isImageItem(item: LayoutItem): item is ImageItem {
  return item.type === "image";
}

export function isClipItem(item: LayoutItem): item is ClipItem {
  return item.type === "clip";
}

export function isTitleItem(item: LayoutItem): item is TitleItem {
  return item.type === "title" || item.type === undefined;
}

/** Returns true for any fullscreen overlay (fullscreen images or clips). */
export function isFullscreenOverlay(item: LayoutItem): item is ImageItem | ClipItem {
  if (isClipItem(item)) return true;
  if (isImageItem(item) && item.display === "fullscreen") return true;
  return false;
}

// ─── Overlap validation ──────────────────────────────────────────────────────

const OVERLAP_BUFFER = 2; // seconds

export function validateNoOverlap(items: LayoutItem[]): string[] {
  const errors: string[] = [];
  const fullscreenOverlays = items.filter(isFullscreenOverlay);
  const titles = items.filter(isTitleItem);

  // Titles cannot overlap with any fullscreen overlay
  for (const overlay of fullscreenOverlays) {
    for (const title of titles) {
      if (title.start < overlay.end + OVERLAP_BUFFER && title.end > overlay.start - OVERLAP_BUFFER) {
        errors.push(
          `Overlap: ${overlay.type} "${overlay.id}" [${overlay.start}-${overlay.end}s] conflicts with title "${title.id}" [${title.start}-${title.end}s]`
        );
      }
    }
  }

  // Fullscreen overlays cannot overlap with each other
  for (let i = 0; i < fullscreenOverlays.length; i++) {
    for (let j = i + 1; j < fullscreenOverlays.length; j++) {
      const a = fullscreenOverlays[i];
      const b = fullscreenOverlays[j];
      if (a.start < b.end + OVERLAP_BUFFER && a.end > b.start - OVERLAP_BUFFER) {
        errors.push(
          `Overlap: ${a.type} "${a.id}" [${a.start}-${a.end}s] conflicts with ${b.type} "${b.id}" [${b.start}-${b.end}s]`
        );
      }
    }
  }

  return errors;
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
