#!/usr/bin/env python3
"""Genera el PDF del informe del pipeline de Motion Graphics automatizado."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
import datetime

OUTPUT_PATH = Path(__file__).parent / "Informe_Pipeline_Motion_Graphics.pdf"

# ─── Colors ───────────────────────────────────────────────────────────────────
GRIKY_BLUE = HexColor("#1a73e8")
GRIKY_DARK = HexColor("#202124")
GRIKY_GRAY = HexColor("#5f6368")
GRIKY_LIGHT = HexColor("#f8f9fa")
WHITE = HexColor("#ffffff")
ACCENT = HexColor("#34a853")

# ─── Styles ───────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="CoverTitle",
    fontName="Helvetica-Bold",
    fontSize=28,
    leading=34,
    textColor=GRIKY_BLUE,
    alignment=TA_CENTER,
    spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="CoverSubtitle",
    fontName="Helvetica",
    fontSize=14,
    leading=18,
    textColor=GRIKY_GRAY,
    alignment=TA_CENTER,
    spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="SectionTitle",
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=GRIKY_BLUE,
    spaceBefore=20,
    spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="SubSection",
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=16,
    textColor=GRIKY_DARK,
    spaceBefore=14,
    spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="BodyText2",
    fontName="Helvetica",
    fontSize=11,
    leading=15,
    textColor=GRIKY_DARK,
    alignment=TA_JUSTIFY,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="BulletItem",
    fontName="Helvetica",
    fontSize=11,
    leading=15,
    textColor=GRIKY_DARK,
    leftIndent=20,
    spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="StepNumber",
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=GRIKY_BLUE,
    spaceBefore=10,
    spaceAfter=2,
))
styles.add(ParagraphStyle(
    name="CodeBlock",
    fontName="Courier",
    fontSize=9,
    leading=12,
    textColor=GRIKY_DARK,
    backColor=GRIKY_LIGHT,
    leftIndent=15,
    rightIndent=15,
    spaceBefore=6,
    spaceAfter=10,
    borderPadding=8,
))
styles.add(ParagraphStyle(
    name="Footer",
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    textColor=GRIKY_GRAY,
    alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="TableHeader",
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    textColor=WHITE,
    alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="TableCell",
    fontName="Helvetica",
    fontSize=10,
    leading=13,
    textColor=GRIKY_DARK,
))


def hr():
    return HRFlowable(width="100%", thickness=1, color=HexColor("#dadce0"),
                       spaceAfter=10, spaceBefore=5)


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        leftMargin=1*inch,
        rightMargin=1*inch,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch,
    )

    story = []
    today = datetime.date.today().strftime("%d de %B de %Y")

    # ═══════════════════════════════════════════════════════════════════════════
    # PORTADA
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Pipeline de Motion Graphics<br/>Automatizado con IA", styles["CoverTitle"]))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Griky — Laboratorio de IA", styles["CoverSubtitle"]))
    story.append(Paragraph(today, styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.5*inch))
    story.append(hr())
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "Este documento explica como funciona la herramienta que genera "
        "automaticamente los textos animados para los videos educativos de Griky, "
        "usando inteligencia artificial.",
        styles["BodyText2"]
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. QUE ES ESTO
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("1. Que es esto y para que sirve", styles["SectionTitle"]))
    story.append(hr())
    story.append(Paragraph(
        "Cuando Griky produce un video educativo, el presentador (avatar) aparece en el centro "
        "y a los lados se muestran titulos animados que resaltan los puntos clave de lo que "
        "esta diciendo. Hasta ahora, esos titulos se escribian a mano en un archivo JSON, "
        "revisando el video segundo a segundo.",
        styles["BodyText2"]
    ))
    story.append(Paragraph(
        "Este pipeline automatiza ese proceso: le das un video y la herramienta produce "
        "automaticamente los titulos, los tiempos exactos en que aparecen, y los iconos "
        "que los acompanian. Todo usando inteligencia artificial.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Antes vs. Ahora", styles["SubSection"]))

    comparison_data = [
        [Paragraph("<b>Antes (manual)</b>", styles["TableHeader"]),
         Paragraph("<b>Ahora (automatizado)</b>", styles["TableHeader"])],
        [Paragraph("Ver el video completo tomando notas", styles["TableCell"]),
         Paragraph("Ejecutar un solo comando", styles["TableCell"])],
        [Paragraph("Escribir cada titulo a mano en JSON", styles["TableCell"]),
         Paragraph("La IA escucha el audio y decide los titulos", styles["TableCell"])],
        [Paragraph("Calcular tiempos manualmente (segundos)", styles["TableCell"]),
         Paragraph("Los tiempos se detectan del audio automaticamente", styles["TableCell"])],
        [Paragraph("Elegir iconos uno por uno", styles["TableCell"]),
         Paragraph("La IA selecciona el icono mas adecuado", styles["TableCell"])],
        [Paragraph("~30-45 minutos por video", styles["TableCell"]),
         Paragraph("~2 minutos por video", styles["TableCell"])],
    ]
    t = Table(comparison_data, colWidths=[2.8*inch, 2.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GRIKY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('BACKGROUND', (0, 1), (-1, -1), GRIKY_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#dadce0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. COMO FUNCIONA (para no-tecnicos)
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("2. Como funciona (explicacion simple)", styles["SectionTitle"]))
    story.append(hr())
    story.append(Paragraph(
        "El proceso tiene 4 pasos, todos automaticos. Tu solo ejecutas un comando "
        "y esperas el resultado:",
        styles["BodyText2"]
    ))

    steps = [
        ("Paso 1: Extraer el audio",
         "La herramienta toma el video MP4 y extrae solamente el audio, "
         "como si le quitaras la imagen y dejaras solo la voz del presentador."),
        ("Paso 2: Transcribir lo que dice",
         "El audio se envia a un servicio de inteligencia artificial (Whisper de Groq) "
         "que escucha todo lo que dice el presentador y lo convierte en texto escrito, "
         "con la marca exacta de en que segundo dice cada frase."),
        ("Paso 3: La IA elige los titulos",
         "Otro modelo de IA (Llama 3 de Groq) lee la transcripcion completa y decide: "
         "cuales son los 6-10 puntos mas importantes del video, que texto corto "
         "los resume mejor, en que momento deben aparecer, en que lado de la pantalla, "
         "y que icono los acompania."),
        ("Paso 4: Generar el archivo final",
         "Toda esa informacion se empaqueta en un archivo JSON que el motor de video "
         "(Remotion) sabe leer para producir el video final con los titulos animados."),
    ]

    for title, desc in steps:
        story.append(Paragraph(title, styles["StepNumber"]))
        story.append(Paragraph(desc, styles["BodyText2"]))

    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        "Diagrama del flujo:",
        styles["SubSection"]
    ))
    story.append(Paragraph(
        "Video MP4 &rarr; Extraer audio &rarr; Transcribir con IA &rarr; "
        "Generar titulos con IA &rarr; Archivo JSON &rarr; Video con motion graphics",
        styles["CodeBlock"]
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. COMO USARLO
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("3. Como usar la herramienta", styles["SectionTitle"]))
    story.append(hr())

    story.append(Paragraph("Requisitos previos (solo la primera vez)", styles["SubSection"]))
    reqs = [
        "Tener Python instalado en tu computador (version 3.10 o superior)",
        "Tener Node.js instalado (version 18 o superior)",
        "Tener ffmpeg instalado (se instala con: winget install Gyan.FFmpeg)",
        "Tener una cuenta gratuita en Groq (groq.com) para obtener tu API key",
    ]
    for r in reqs:
        story.append(Paragraph(f"&bull; {r}", styles["BulletItem"]))

    story.append(Paragraph("Configuracion inicial (solo la primera vez)", styles["SubSection"]))
    setup_steps = [
        "Abre una terminal y navega a la carpeta del proyecto:",
        "cd avatar-titles-remotion/scripts",
        "Instala las dependencias de Python:",
        "pip install -r requirements.txt",
        "Copia el archivo .env.example y renombralo a .env",
        "Abre .env con un editor de texto y pega tu API key de Groq donde dice gsk_your_key_here",
    ]
    for i, s in enumerate(setup_steps):
        if i % 2 == 0:
            story.append(Paragraph(f"<b>{i//2 + 1}.</b> {s}", styles["BodyText2"]))
        else:
            story.append(Paragraph(s, styles["CodeBlock"]))

    story.append(Paragraph("Generar los titulos para un video", styles["SubSection"]))
    story.append(Paragraph(
        "Cada vez que quieras procesar un video nuevo, solo necesitas ejecutar este comando:",
        styles["BodyText2"]
    ))
    story.append(Paragraph(
        'python generate_layout.py --video "../public/nombre-del-video.mp4"',
        styles["CodeBlock"]
    ))
    story.append(Paragraph(
        "La herramienta te ira mostrando el progreso en la terminal: extrayendo audio, "
        "transcribiendo, generando titulos... Al final te dira donde guardo el archivo JSON.",
        styles["BodyText2"]
    ))

    story.append(Paragraph("Ver el resultado en el previsualizador", styles["SubSection"]))
    story.append(Paragraph(
        "Para ver como quedo el video con los titulos animados:",
        styles["BodyText2"]
    ))
    preview_steps = [
        ("1.", "Abre otra terminal en la carpeta avatar-titles-remotion"),
        ("2.", "Ejecuta: <b>npm start</b>"),
        ("3.", "Se abrira el navegador en localhost:3000 (Remotion Studio)"),
        ("4.", "En el panel izquierdo, selecciona la composicion con el nombre de tu video"),
        ("5.", "Dale play para ver el video con los titulos animados"),
        ("6.", "Si quieres ajustar algun titulo o tiempo, edita el archivo JSON en src/data/"),
    ]
    for num, text in preview_steps:
        story.append(Paragraph(f"<b>{num}</b> {text}", styles["BodyText2"]))

    story.append(Paragraph("Exportar el video final", styles["SubSection"]))
    story.append(Paragraph(
        "Cuando estes satisfecho con el resultado, exporta el video final:",
        styles["BodyText2"]
    ))
    story.append(Paragraph(
        "npx remotion render NombreComposicion out/mi-video.mp4",
        styles["CodeBlock"]
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 4. RESULTADO DEL PRIMER TEST
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("4. Resultado de la primera prueba", styles["SectionTitle"]))
    story.append(hr())
    story.append(Paragraph(
        "Se probo la herramienta con el video T1 sobre Modelado Relacional en Power BI "
        "(117 segundos de duracion). La IA genero 10 titulos automaticamente:",
        styles["BodyText2"]
    ))

    items_data = [
        [Paragraph("<b>#</b>", styles["TableHeader"]),
         Paragraph("<b>Titulo generado</b>", styles["TableHeader"]),
         Paragraph("<b>Aparece</b>", styles["TableHeader"]),
         Paragraph("<b>Lado</b>", styles["TableHeader"]),
         Paragraph("<b>Icono</b>", styles["TableHeader"])],
        ["h1", "Modelo incorrecto", "seg. 2-6", "Izq.", "Alerta"],
        ["h2", "Esquema estrella", "seg. 17-21", "Der.", "Estrella"],
        ["h3", "Filtros unidireccionales", "seg. 27-31", "Izq.", "Flecha"],
        ["h4", "Modelo roto vs correcto", "seg. 36-40", "Der.", "Bifurcacion"],
        ["h5", "Resultado diferente", "seg. 56-60", "Izq.", "Intercambio"],
        ["h6", "3 pasos de correccion", "seg. 62-66", "Der.", "Herramienta"],
        ["h6a", "1. Relaciones unidireccionales", "seg. 63-65", "Der.", "-"],
        ["h6b", "2. Elimina relacion triangular", "seg. 73-75", "Der.", "-"],
        ["h6c", "3. Verifica 1 y *", "seg. 77-79", "Der.", "-"],
        ["h7", "Seniales de problemas", "seg. 85-89", "Izq.", "Alerta roja"],
    ]
    # Convert plain rows to Paragraph cells
    for i in range(1, len(items_data)):
        items_data[i] = [Paragraph(str(c), styles["TableCell"]) for c in items_data[i]]

    t2 = Table(items_data, colWidths=[0.4*inch, 2.2*inch, 1*inch, 0.6*inch, 1*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GRIKY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('BACKGROUND', (0, 1), (-1, -1), GRIKY_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#dadce0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "La IA acerto en los mismos conceptos clave que el JSON creado manualmente, "
        "eligio los mismos iconos, y ubico los titulos en tiempos muy similares. "
        "El resultado es practicamente identico al trabajo manual, pero generado en 2 minutos "
        "en lugar de 30-45 minutos.",
        styles["BodyText2"]
    ))

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. QUE FALTA / PROXIMOS PASOS
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("5. Proximos pasos y mejoras pendientes", styles["SectionTitle"]))
    story.append(hr())

    next_items = [
        ("Registro automatico en Root.tsx",
         "Actualmente hay que agregar manualmente la nueva composicion al archivo Root.tsx. "
         "Se puede automatizar para que el script lo haga solo."),
        ("Procesamiento por lotes",
         "Poder pasar una carpeta con varios videos y que genere todos los JSON de una vez."),
        ("Interfaz web sencilla",
         "Crear una pagina web donde se suba el video y se descargue el JSON, "
         "sin necesidad de usar la terminal."),
        ("Ajuste fino del prompt",
         "Mejorar las instrucciones que se le dan a la IA para que los titulos sean "
         "aun mas precisos y editorialmente pulidos."),
        ("Soporte multi-idioma",
         "Actualmente funciona en espaniol e ingles. Se puede extender a otros idiomas."),
    ]
    for title, desc in next_items:
        story.append(Paragraph(f"&bull; <b>{title}:</b> {desc}", styles["BulletItem"]))

    # ═══════════════════════════════════════════════════════════════════════════
    # 6. TECNOLOGIAS USADAS
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("6. Tecnologias usadas", styles["SectionTitle"]))
    story.append(hr())

    tech_data = [
        [Paragraph("<b>Tecnologia</b>", styles["TableHeader"]),
         Paragraph("<b>Para que se usa</b>", styles["TableHeader"]),
         Paragraph("<b>Costo</b>", styles["TableHeader"])],
        [Paragraph("ffmpeg", styles["TableCell"]),
         Paragraph("Extraer audio del video", styles["TableCell"]),
         Paragraph("Gratis", styles["TableCell"])],
        [Paragraph("Groq Whisper", styles["TableCell"]),
         Paragraph("Convertir audio a texto con tiempos", styles["TableCell"]),
         Paragraph("Gratis (API)", styles["TableCell"])],
        [Paragraph("Groq Llama 3", styles["TableCell"]),
         Paragraph("Decidir que titulos mostrar", styles["TableCell"]),
         Paragraph("Gratis (API)", styles["TableCell"])],
        [Paragraph("Python", styles["TableCell"]),
         Paragraph("Script que conecta todo", styles["TableCell"]),
         Paragraph("Gratis", styles["TableCell"])],
        [Paragraph("Remotion", styles["TableCell"]),
         Paragraph("Generar el video con animaciones", styles["TableCell"]),
         Paragraph("Gratis (local)", styles["TableCell"])],
    ]
    t3 = Table(tech_data, colWidths=[1.5*inch, 2.8*inch, 1*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GRIKY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('BACKGROUND', (0, 1), (-1, -1), GRIKY_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#dadce0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t3)

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "<b>Costo total del pipeline: $0.</b> Todas las herramientas usadas son gratuitas.",
        styles["BodyText2"]
    ))

    # ═══════════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.5*inch))
    story.append(hr())
    story.append(Paragraph(
        f"Griky — Laboratorio de IA — {today}",
        styles["Footer"]
    ))

    doc.build(story)
    print(f"PDF generado: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
