# Avatar Side Titles — Documentación

Herramienta de motion graphics para vídeos educativos. Superpone títulos animados a izquierda y derecha de un presenter (avatar) de forma sincronizada con el audio, totalmente controlada por un archivo JSON.

**Stack:** React · TypeScript · Remotion · Google Fonts (Roboto) · react-icons (Feather)

---

## Qué produce

Un vídeo 1920×1080 (o las dimensiones que definas) con:
- El vídeo del presenter al fondo
- Títulos animados en columna izquierda y/o derecha
- Iconos encima de cada título (opcionales)
- Animaciones de entrada/salida frame-perfect

También puede exportar **solo los títulos con canal alpha** (`.webm`) para compositar en Premiere, DaVinci o After Effects.

---

## Flujo de trabajo

```
1. Coloca el vídeo del presenter en public/
2. Edita el JSON con los títulos y timings
3. npm start → previsualiza en Remotion Studio (localhost:3000)
4. Ajusta timings/texto en el JSON
5. remotion render → exporta el .mp4 final
```

---

## Arranque rápido

```bash
npm install
npm start           # Remotion Studio
```

En Mac también puedes hacer doble clic en **`Abrir Studio.command`**.

---

## Estructura del proyecto

```
avatar-titles-remotion/
├── public/                          ← assets de vídeo del presenter
│   └── avatar.mp4
├── src/
│   ├── Root.tsx                     ← registra composiciones Remotion
│   ├── AvatarSideTitles.tsx         ← componente principal del canvas
│   ├── index.ts                     ← entry point
│   ├── components/
│   │   └── TitleBlock.tsx           ← bloque de título con animación
│   ├── lib/
│   │   ├── layout.ts                ← tipos, helpers, estilos por variante
│   │   └── icons.ts                 ← mapa nombre → componente de icono
│   └── data/
│       ├── sample-video-layout.json      ← demo v1
│       ├── sample-video-layout-v2.json   ← demo v2
│       └── t1-modelado-relacional.json   ← producción real (T1 Power BI)
├── out/                             ← vídeos renderizados
├── docs/
│   └── documentacion.md             ← este archivo
├── remotion.config.ts
├── package.json
└── tsconfig.json
```

---

## El archivo JSON

Cada composición se define con un único JSON. Para crear un vídeo nuevo, crea un nuevo `.json` en `src/data/` e impórtalo en `Root.tsx`.

### Estructura completa

```json
{
  "videoSrc": "nombre-del-archivo.mp4",
  "canvas": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "durationInSeconds": 120
  },
  "layout": {
    "left":   { "x": 80,   "y": 140, "width": 480, "height": 800 },
    "center": { "x": 640,  "y": 0,   "width": 640, "height": 1080 },
    "right":  { "x": 1360, "y": 140, "width": 480, "height": 800 }
  },
  "items": [ ... ]
}
```

### Zonas del canvas (1920×1080 por defecto)

```
| ← 80px → | ←— LEFT (480px) —→ | ←— CENTER (640px) —→ | ←— RIGHT (480px) —→ | ← 80px → |
                 col izquierda          avatar / vídeo          col derecha
```

### Campos de cada título (`items[]`)

| Campo | Tipo | Valores | Descripción |
|---|---|---|---|
| `id` | string | único | Identificador del bloque |
| `text` | string | — | Texto a mostrar |
| `icon` | string | nombre Feather | Icono encima del texto (opcional) |
| `start` | number | segundos | Cuándo aparece |
| `end` | number | segundos | Cuándo desaparece |
| `column` | string | `"left"` · `"right"` | Columna donde se pinta |
| `verticalAlign` | string | `"top"` · `"center"` · `"bottom"` | Posición vertical en la columna |
| `variant` | string | `"headline"` · `"subheadline"` | Tamaño tipográfico |
| `animationIn` | string | `"slideRightFade"` · `"slideLeftFade"` · `"fadeIn"` | Animación de entrada |
| `animationOut` | string | `"fadeOut"` | Animación de salida |

### Variantes tipográficas

| Variante | Tamaño | Peso | Uso recomendado |
|---|---|---|---|
| `headline` | 64px | 800 | Concepto principal del segmento |
| `subheadline` | 36px | 500 | Puntos de apoyo, listas, pasos |

### Iconos disponibles

Cualquier icono de [Feather Icons](https://feathericons.com/), referenciado por su nombre en PascalCase con prefijo `Fi`:

```
FiAlertTriangle  FiStar  FiArrowRight  FiGitMerge
FiShuffle  FiTool  FiAlertOctagon  FiCheckCircle
FiPlay  FiBook  FiClock  FiTarget  FiTrendingUp  ...
```

---

## Renderizado

### MP4 estándar (con vídeo de avatar)

```bash
npx remotion render NombreComposicion out/mi-video.mp4
```

### Solo títulos con canal alpha (para compositar externamente)

1. En `src/AvatarSideTitles.tsx`, cambia `SHOW_PREVIEW_BACKGROUND = false`
2. Comenta el bloque `<OffthreadVideo>` si no quieres el avatar

```bash
npx remotion render NombreComposicion out/titulos-alpha.webm \
  --codec=vp8 --pixel-format=yuva420p
```

El `.webm` resultante tiene canal alpha y puede arrastrarse como capa en cualquier editor de vídeo.

---

## Añadir una composición nueva

1. Crea `src/data/mi-video.json` con la estructura descrita arriba
2. Importa y registra en `src/Root.tsx`:

```tsx
import miVideo from "./data/mi-video.json";

// dentro de <RemotionRoot>:
<TypedComposition
  id="MiVideo"
  component={AvatarSideTitles}
  width={miVideo.canvas.width}
  height={miVideo.canvas.height}
  fps={miVideo.canvas.fps}
  durationInFrames={miVideo.canvas.durationInSeconds * miVideo.canvas.fps}
  defaultProps={miVideo as VideoLayout}
/>
```

---

## Composiciones actuales

| ID | Archivo JSON | Descripción |
|---|---|---|
| `T1GeneradoIA` | `t1-modelado-relacional-en-power-bi-b.json` | T1 Power BI · generado por IA · 10 títulos |
| `T1ModeladoRelacional` | `t1-modelado-relacional.json` | T1 Power BI · 117s · 10 títulos (manual) |
| `AvatarSideTitlesDemo` | `sample-video-layout.json` | Demo v1 |
| `AvatarSideTitlesDemoV2` | `sample-video-layout-v2.json` | Demo v2 |

---

## Animaciones — detalle técnico

Cada `TitleBlock` calcula sus propias curvas frame a frame con `interpolate` de Remotion:

| Parámetro | Valor |
|---|---|
| Frames de entrada (`ANIM_IN_FRAMES`) | 18 frames (~0.6s a 30fps) |
| Frames de salida (`ANIM_OUT_FRAMES`) | 12 frames (~0.4s a 30fps) |
| Distancia de slide (`SLIDE_DISTANCE`) | 48px |

- `slideRightFade`: entra desde la izquierda (x: −48 → 0) con fade in
- `slideLeftFade`: entra desde la derecha (x: +48 → 0) con fade in
- `fadeIn`: solo opacidad, sin desplazamiento
- La salida es siempre `fadeOut` (opacidad 1 → 0)

---

## Pipeline de generación automática con IA

### Descripción

Script Python que automatiza la creación del JSON de títulos a partir de un video MP4. Usa inteligencia artificial para transcribir el audio y generar los highlights editoriales.

### Arquitectura

```
Video MP4
    │
    ▼
[ffmpeg] extrae audio → audio.mp3 (mono, 16kHz)
    │
    ▼
[Groq Whisper] transcribe → segments[] con timestamps
    │
    ▼
[Groq Llama 3] + prompt editorial → items[] JSON
    │
    ▼
Ensambla VideoLayout JSON → src/data/{nombre}.json
    │
    ▼
Remotion renderiza → video final con motion graphics
```

### Estructura de archivos del pipeline

```
avatar-titles-remotion/
├── scripts/
│   ├── generate_layout.py      ← script principal (CLI)
│   ├── prompt_template.txt     ← prompt editorial para el LLM
│   ├── requirements.txt        ← dependencias Python
│   ├── .env.example            ← template de variables de entorno
│   └── .env                    ← API key real (gitignored)
├── transcripts/
│   ├── .gitkeep
│   ├── {nombre}_audio.mp3      ← cache de audio extraído
│   └── {nombre}_transcript.json ← cache de transcripción
└── ...
```

### Requisitos

- Python 3.10+
- ffmpeg instalado (`winget install Gyan.FFmpeg`)
- Cuenta Groq gratuita con API key (https://console.groq.com)

### Instalación

```bash
cd avatar-titles-remotion/scripts
pip install -r requirements.txt
cp .env.example .env
# Editar .env y agregar tu GROQ_API_KEY
```

### Uso

```bash
# Generar JSON para un video
python generate_layout.py --video "../public/nombre-del-video.mp4"

# Forzar re-transcripción (ignora cache)
python generate_layout.py --video "../public/video.mp4" --force-transcribe

# Especificar nombre de salida
python generate_layout.py --video "../public/video.mp4" --output mi-video

# Si ya conoces la duración (evita ffprobe)
python generate_layout.py --video "../public/video.mp4" --duration 117
```

### Modelos de IA utilizados

| Modelo | Proveedor | Uso | Costo |
|---|---|---|---|
| `whisper-large-v3-turbo` | Groq | Transcripción de audio a texto | Gratis |
| `llama-3.3-70b-versatile` | Groq | Generación de títulos editoriales | Gratis |

### Prompt editorial

El archivo `scripts/prompt_template.txt` contiene las instrucciones que recibe la IA para generar los títulos. Reglas principales:

- 6-10 highlights por video
- Texto máximo 8 palabras, corto y editorial
- Mismo idioma que el video
- Columnas alternadas: izq, der, izq, der...
- 4-5 segundos visible por título
- Mínimo 2 segundos de separación entre títulos
- Iconos de los 35 disponibles en `src/lib/icons.ts`
- Soporte para subheadlines (pasos, listas)

### Cache

El pipeline guarda resultados intermedios en `transcripts/`:
- Audio extraído: no re-extrae si ya existe
- Transcripción: no re-transcribe si ya existe (usar `--force-transcribe` para forzar)

### Auto-registro en Root.tsx

El script registra automáticamente la nueva composición en `src/Root.tsx` (import + cast + `<TypedComposition>`). No es necesario hacerlo manualmente.

Para desactivar: `--no-register`

### Procesamiento por lotes

```bash
# Procesar todos los MP4 de una carpeta
python generate_layout.py --batch "../public/"
python generate_layout.py --batch "C:/Users/MiUsuario/Desktop/videos/"
```

Cada vídeo genera su JSON y se registra automáticamente. Al final muestra resumen OK/FAILED.

### ffmpeg auto-discovery

El script busca ffmpeg automáticamente sin depender del PATH del sistema:
1. Primero verifica si está en PATH
2. Si no, busca en WinGet packages (`AppData/Local/Microsoft/WinGet/Packages/`)
3. Si no, busca en `C:\ffmpeg\bin\` y `D:\ffmpeg\bin\`

### Resultado del primer test (T1 Modelado Relacional)

El pipeline generó 10 títulos para el video T1 (117s) que coinciden casi exactamente con los del JSON manual:

| IA generó | Manual tenía | Match |
|---|---|---|
| "Modelo incorrecto" (s.2) | "Números incorrectos sin saberlo" (s.2) | ✓ mismo concepto, mismo tiempo |
| "Esquema estrella" (s.17) | "El esquema estrella" (s.17) | ✓ idéntico |
| "Filtros unidireccionales" (s.27) | "Filtros en una sola dirección" (s.27) | ✓ mismo concepto |
| "3 pasos de corrección" + 3 subs | "3 pasos para corregir el modelo" + 3 subs | ✓ estructura idéntica |
