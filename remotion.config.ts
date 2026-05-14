import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

/**
 * EXPORTACIÓN TRANSPARENTE (alpha channel)
 *
 * Remotion soporta exportar vídeo con canal alpha (transparencia) usando:
 *
 *   remotion render AvatarSideTitlesDemo out/video-alpha.webm \
 *     --codec=vp8 \
 *     --pixel-format=yuva420p
 *
 * O con VP9:
 *   --codec=vp9 --pixel-format=yuva420p
 *
 * Para que la transparencia sea real:
 * 1. El fondo del canvas debe ser transparent (no color sólido).
 * 2. En AvatarSideTitles.tsx, desactiva SHOW_PREVIEW_BACKGROUND o ponlo en false.
 * 3. Usa el script "build:transparent" del package.json.
 *
 * El script ya está configurado en package.json como:
 *   "build:transparent": "remotion render AvatarSideTitlesDemo out/video-alpha.webm --codec=vp8 --pixel-format=yuva420p"
 */
