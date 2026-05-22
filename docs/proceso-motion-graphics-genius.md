# Proceso: Motion Graphics Automatizados para Videos con Avatar

## Resumen del proceso

Este pipeline genera automáticamente overlays animados (títulos, imágenes y clips de video) sobre videos educativos con avatar. La IA analiza el transcript del video y decide qué momentos destacar visualmente.

**Input**: Video .mp4 con avatar hablando
**Output**: Video .mp4 con motion graphics profesionales superpuestos

## Filosofía de diseño

| Elemento | % del video | Descripción |
|----------|-------------|-------------|
| Avatar visible | ~30% | El speaker aparece en pantalla |
| Imágenes fullscreen | ~35% | Infografías, datos, diagramas (generadas con IA) |
| Clips fullscreen | ~35% | Videos cortos ilustrativos (generados externamente) |
| Títulos de texto | Solo durante avatar | Frases cortas con ícono, aparecen a los lados |

El avatar solo se ve ~30% del tiempo. El resto está cubierto por contenido visual que refuerza lo que dice el speaker.

## Stack tecnológico

| Componente | Tecnología | Función |
|------------|-----------|---------|
| Rendering | Remotion 4 + React + TypeScript | Genera el video final |
| Transcripción | Groq Whisper API | Convierte audio a texto con timestamps |
| Generación de items | Groq LLM (Llama 3.3 70B) | Decide qué overlays poner y cuándo |
| Imágenes | DALL-E / Midjourney (externo) | Genera las imágenes a partir de prompts |
| Clips | Herramienta de video IA (externo) | Genera clips a partir de prompts |

## Prerequisitos

1. **Node.js** >= 18
2. **Python** >= 3.10 con pip
3. **ffmpeg** instalado (`winget install Gyan.FFmpeg`)
4. **API Key de Groq** (gratuita en https://console.groq.com)

## Setup inicial (una sola vez)

```bash
# 1. Entrar al proyecto
cd avatar-titles-remotion

# 2. Instalar dependencias Node
npm install

# 3. Instalar dependencias Python
cd scripts
pip install -r requirements.txt

# 4. Configurar API key
cp .env.example .env
# Editar .env y poner tu GROQ_API_KEY
```

## Workflow paso a paso

### Paso 1 — Organizar el video

Colocar el video .mp4 en la estructura de carpetas dentro de `public/`:

```
public/
└── {diplomado}/
    └── {curso}/
        └── {unidad}/
            └── mi-video.mp4
```

**Ejemplo**: `public/accclimatica/curso1/u1/t3.mp4`

### Paso 2 — Ejecutar el pipeline de IA

```bash
cd scripts
python generate_layout.py --video ../public/accclimatica/curso1/u1/t3.mp4
```

Esto hace automáticamente:
1. Extrae el audio del video (ffmpeg)
2. Transcribe con Groq Whisper
3. La IA analiza el transcript y genera un JSON con los overlays
4. Guarda el JSON en `src/data/`
5. Registra la composición en Remotion

**Opciones útiles**:
- `--interactive` o `-i`: modo interactivo para revisar/editar items después de la generación
- `--force-transcribe`: re-transcribir aunque ya exista cache
- `--no-register`: no registrar automáticamente en Root.tsx

### Paso 3 — Preview en Remotion Studio

```bash
npm start
```

Abre http://localhost:3000. Selecciona la composición del sidebar. Verás:
- **Títulos** animados a los lados del avatar
- **Placeholders** de imágenes (cuadro punteado con prompt)
- **Placeholders** de clips (cuadro punteado con prompt)

### Paso 4 — Generar assets visuales

El JSON tiene items con `"src": "NEEDS_IMAGE"` y `"src": "NEEDS_CLIP"`. Cada uno incluye un prompt descriptivo.

**Para imágenes** (`imagePrompt`):
1. Copiar el `imagePrompt` del JSON
2. Pegarlo en DALL-E, Midjourney, o herramienta de generación de imágenes
3. Guardar la imagen en la misma carpeta del video: `public/accclimatica/curso1/u1/img1.png`

**Para clips** (`clipPrompt`):
1. Copiar el `clipPrompt` del JSON
2. Usar herramienta de generación de video (Runway, Pika, etc.)
3. Guardar el clip en la misma carpeta: `public/accclimatica/curso1/u1/clip1.mp4`

### Paso 5 — Actualizar el JSON con rutas reales

Editar el JSON en `src/data/` y reemplazar los placeholders:

```json
// Antes:
"src": "NEEDS_IMAGE"

// Después:
"src": "accclimatica/curso1/u1/img1.png"
```

Las rutas son relativas a `public/`.

### Paso 6 — Render final

```bash
npx remotion render T3 out/t3-final.mp4
```

Para mejor rendimiento: `npx remotion render T3 out/t3.mp4 --concurrency=4`

## Tipos de overlay

### Títulos (text + ícono)
- Aparecen a la izquierda o derecha del avatar
- Texto corto (máx 8 palabras) + ícono de Feather Icons
- Animación slide + fade
- Solo durante los momentos donde el avatar es visible

### Imágenes (fullscreen)
- Cubren toda la pantalla, el avatar se oculta
- Infografías, gráficos, datos visuales
- Estética oscura y cálida (tonos ámbar, dorado, fondo #1a1a2e)
- Transición crossfade suave

### Clips (fullscreen)
- Videos cortos que cubren toda la pantalla
- Siempre muteados (el audio del avatar sigue sonando)
- Procesos, demos, secuencias visuales
- Misma transición crossfade que las imágenes

## Estilo visual

Todas las imágenes generadas deben seguir esta estética:
- **Fondo**: oscuro cálido (#1a1a2e a #2d1b00)
- **Acentos**: ámbar (#F59E0B), dorado (#D4A574), teal (#5EEAD4)
- **Tipografía**: sans-serif (Roboto)
- **Estilo**: infografía corporativa premium, cinematográfica
- **NO**: fondos blancos, clip-art, colores primarios brillantes

## Estructura del JSON

```json
{
  "videoSrc": "accclimatica/curso1/u1/t3.mp4",
  "canvas": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "durationInSeconds": 188
  },
  "layout": {
    "left":   { "x": 80,   "y": 140, "width": 480, "height": 800 },
    "center": { "x": 640,  "y": 0,   "width": 640, "height": 1080 },
    "right":  { "x": 1360, "y": 140, "width": 480, "height": 800 }
  },
  "items": [
    {
      "type": "title",
      "id": "h1",
      "text": "Título corto",
      "icon": "FiZap",
      "start": 5,
      "end": 9,
      "column": "left",
      "verticalAlign": "center",
      "variant": "headline",
      "animationIn": "slideRightFade",
      "animationOut": "fadeOut"
    },
    {
      "type": "image",
      "id": "img1",
      "src": "NEEDS_IMAGE",
      "imagePrompt": "Descripción para generar la imagen...",
      "start": 12,
      "end": 20,
      "display": "fullscreen",
      "animationIn": "fadeIn",
      "animationOut": "fadeOut"
    },
    {
      "type": "clip",
      "id": "clip1",
      "src": "NEEDS_CLIP",
      "clipPrompt": "Descripción del clip ideal...",
      "start": 25,
      "end": 33,
      "display": "fullscreen",
      "animationIn": "fadeIn",
      "animationOut": "fadeOut"
    }
  ]
}
```

## Modo interactivo

Para editar items después de la generación:

```bash
python generate_layout.py --video ../public/video.mp4 --interactive
```

O editar un JSON existente:
```bash
python generate_layout.py --edit ../src/data/t3.json
```

Comandos disponibles:
| Comando | Descripción |
|---------|-------------|
| `show` | Ver timeline + gaps |
| `transcript 10 30` | Ver transcript entre 10s y 30s |
| `add-title 15 19 Mi título` | Agregar título manualmente |
| `add-image 20 28` | Agregar imagen con prompt generado por IA |
| `fill-gaps` | IA genera títulos para todos los gaps > 10s |
| `fill 40 60` | IA genera títulos para un rango específico |
| `edit h1 text Nuevo texto` | Editar campo de un item |
| `remove h3` | Eliminar un item |
| `done` | Guardar y salir |

## Procesamiento por lotes

```bash
python generate_layout.py --batch ../public/accclimatica/curso1/u1/
```

Procesa todos los .mp4 en la carpeta secuencialmente.

## Troubleshooting

| Problema | Solución |
|----------|----------|
| ffmpeg not found | `winget install Gyan.FFmpeg` |
| Groq API error | Verificar `scripts/.env` tiene GROQ_API_KEY válido |
| Audio > 25 MB | Groq Whisper tiene límite de 25 MB |
| Video no aparece en preview | Verificar que el .mp4 está en `public/` y la ruta en el JSON coincide |
| Error "Cannot read x" en preview | Verificar que items image/clip tienen `"type"` correcto |
| Render lento | Usar `--concurrency=4` o mayor |

## Archivos clave del proyecto

| Archivo | Función |
|---------|---------|
| `scripts/generate_layout.py` | Pipeline completo de IA |
| `scripts/prompt_template.txt` | Prompt que recibe el LLM |
| `src/AvatarSideTitles.tsx` | Componente principal de Remotion |
| `src/components/TitleBlock.tsx` | Renderiza títulos animados |
| `src/components/ImageBlock.tsx` | Renderiza imágenes (fullscreen/PiP/placeholder) |
| `src/components/ClipBlock.tsx` | Renderiza clips de video |
| `src/lib/layout.ts` | Tipos TypeScript y validaciones |
| `src/data/t1-modelado-relacional.json` | JSON de ejemplo que el LLM usa como referencia |
| `CLAUDE.md` | Documentación técnica completa para Claude Code |
