# Motion Graphics GrikyGenius

Pipeline automatizado de motion graphics para videos educativos con avatar. La IA analiza el transcript y genera overlays animados (títulos, imágenes y clips) que se renderizan con Remotion.

**Pipeline**: Video → ffmpeg → Groq Whisper → Groq LLM → JSON → Remotion → MP4

## Filosofia de diseño

El avatar solo es visible ~30% del video. El ~70% restante está cubierto por overlays fullscreen:

| Elemento | Tiempo | Descripción |
|----------|--------|-------------|
| Avatar visible | ~30% | Speaker en pantalla |
| Imágenes | ~35% | Infografías, datos, diagramas |
| Clips | ~35% | Videos cortos ilustrativos |
| Títulos | Durante avatar | Frases cortas + ícono a los lados |

---

## Prerequisitos

| Herramienta | Versión | Instalación |
|-------------|---------|-------------|
| Node.js | >= 18 | [nodejs.org](https://nodejs.org/) |
| Python | >= 3.10 | [python.org](https://www.python.org/downloads/) |
| ffmpeg | reciente | `winget install Gyan.FFmpeg` / `brew install ffmpeg` |
| Groq API key | — | [console.groq.com/keys](https://console.groq.com/keys) |

---

## Setup

```bash
# 1. Clonar e instalar
git clone https://github.com/IngJuanVelGriky/Motion_Graphics_GrikyGenius.git
cd Motion_Graphics_GrikyGenius
npm install

# 2. Dependencias Python
cd scripts
pip install -r requirements.txt

# 3. API key
cp .env.example .env
# Editar .env → agregar GROQ_API_KEY

# 4. Verificar setup
cd ..
npm run setup
```

---

## Workflow

### 1. Colocar el video

Organizar en la estructura de carpetas:
```
public/{diplomado}/{curso}/{unidad}/video.mp4
```
Ejemplo: `public/accclimatica/curso1/u1/t3.mp4`

### 2. Generar overlays con IA

```bash
cd scripts
python generate_layout.py --video ../public/accclimatica/curso1/u1/t3.mp4
```

Opción interactiva (revisar/editar items):
```bash
python generate_layout.py --video ../public/accclimatica/curso1/u1/t3.mp4 -i
```

### 3. Preview

```bash
npm start
```
Abre http://localhost:3000 → seleccionar composición del sidebar.

### 4. Generar assets

El JSON generado tiene placeholders:
- `"src": "NEEDS_IMAGE"` + `imagePrompt` → generar con DALL-E, Midjourney, etc.
- `"src": "NEEDS_CLIP"` + `clipPrompt` → generar con Runway, Pika, etc.

Guardar en la misma carpeta del video y actualizar el JSON con la ruta relativa:
```json
"src": "accclimatica/curso1/u1/img1.png"
```

### 5. Render

```bash
npx remotion render T3 out/t3-final.mp4 --concurrency=4
```

Transparente (para compositing):
```bash
npx remotion render T3 out/t3.webm --codec=vp8 --pixel-format=yuva420p
```

---

## Procesamiento por lotes

```bash
cd scripts
python generate_layout.py --batch ../public/accclimatica/curso1/u1/
```

---

## Estructura del proyecto

```
├── public/                    ← Videos y assets por curso
│   └── {diplomado}/{curso}/{unidad}/
│       ├── video.mp4
│       ├── img1.png
│       └── clip1.mp4
├── src/
│   ├── Root.tsx               ← Registro de composiciones
│   ├── AvatarSideTitles.tsx   ← Componente principal
│   ├── components/
│   │   ├── TitleBlock.tsx     ← Títulos animados
│   │   ├── ImageBlock.tsx     ← Imágenes (fullscreen/PiP/placeholder)
│   │   └── ClipBlock.tsx      ← Clips de video (fullscreen/placeholder)
│   ├── data/
│   │   └── *.json             ← JSONs de layout (uno por video)
│   └── lib/
│       ├── layout.ts          ← Tipos TypeScript
│       └── icons.ts           ← Catálogo de íconos Feather
├── scripts/
│   ├── generate_layout.py     ← Pipeline de IA
│   ├── prompt_template.txt    ← Prompt del LLM
│   └── requirements.txt
├── docs/                      ← Documentación del proceso
├── transcripts/               ← Cache (auto-generado, gitignored)
└── out/                       ← Videos renderizados (gitignored)
```

---

## Tipos de overlay

### Títulos
```json
{
  "type": "title",
  "id": "h1",
  "text": "Título corto",
  "icon": "FiZap",
  "start": 5, "end": 9,
  "column": "left",
  "variant": "headline",
  "animationIn": "slideRightFade",
  "animationOut": "fadeOut"
}
```

### Imágenes
```json
{
  "type": "image",
  "id": "img1",
  "src": "NEEDS_IMAGE",
  "imagePrompt": "Descripción para IA...",
  "start": 12, "end": 20,
  "display": "fullscreen",
  "animationIn": "fadeIn",
  "animationOut": "fadeOut"
}
```

### Clips
```json
{
  "type": "clip",
  "id": "clip1",
  "src": "NEEDS_CLIP",
  "clipPrompt": "Descripción del clip...",
  "start": 25, "end": 33,
  "display": "fullscreen",
  "animationIn": "fadeIn",
  "animationOut": "fadeOut"
}
```

---

## Uso con Claude Code / Claude Desktop

Este proyecto incluye `CLAUDE.md` con la referencia técnica completa. Claude puede:
1. Ejecutar el pipeline completo
2. Editar JSONs
3. Diagnosticar errores
4. Agregar o mover overlays

```
"Genera motion graphics para el video t3.mp4 en accclimatica/curso1/u1"
```

---

## Documentación completa

- `CLAUDE.md` — Referencia técnica, JSON schema, catálogo de íconos
- `docs/proceso-motion-graphics-genius.md` — Proceso paso a paso para el equipo

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| ffmpeg not found | `winget install Gyan.FFmpeg` |
| Groq API error | Verificar `scripts/.env` |
| Audio > 25 MB | Límite de Groq Whisper |
| Error en preview | Verificar `type` en items del JSON |
| Render lento | `--concurrency=4` |
