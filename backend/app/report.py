import io
import os
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Turkce karakterler (s, g, i, o, u, c) icin varsayilan Helvetica yetersiz;
# matplotlib'in kendi pakettiyle gelen DejaVu Sans fontunu kullaniyoruz.
_FONT_DIR = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
pdfmetrics.registerFont(TTFont("DejaVuSans", os.path.join(_FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFontFamily(
    "DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold", italic="DejaVuSans", boldItalic="DejaVuSans-Bold"
)

FONT = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"

plt.rcParams["font.family"] = "DejaVu Sans"


def build_consumption_chart(daily_consumption: list[dict], unit: str) -> io.BytesIO:
    dates = [d["date"] for d in daily_consumption]
    values = [d["quantity"] for d in daily_consumption]

    fig, ax = plt.subplots(figsize=(6.5, 2.8), dpi=150)
    ax.plot(range(len(values)), values, color="#2563eb", linewidth=1.5)
    ax.fill_between(range(len(values)), values, color="#2563eb", alpha=0.08)
    ax.set_ylabel(unit)

    tick_step = max(1, len(dates) // 6)
    ticks = list(range(0, len(dates), tick_step))
    ax.set_xticks(ticks)
    ax.set_xticklabels([dates[i] for i in ticks], rotation=30, ha="right", fontsize=7)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return buffer


def build_comparison_bar_chart(items: list[dict]) -> io.BytesIO:
    names = [i["material_name"] for i in items]
    values = [i["total_consumption"] for i in items]

    fig, ax = plt.subplots(figsize=(6.5, 3.0), dpi=150)
    ax.bar(names, values, color="#2563eb")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=8)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return buffer


def build_summary_report(summary: dict, materials: list[dict], alerts: list[dict], comparison: list[dict]) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], fontName=FONT_BOLD, fontSize=18, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], fontName=FONT, textColor=colors.grey, fontSize=10, spaceAfter=6
    )
    heading_style = ParagraphStyle(
        "HeadingCustom", parent=styles["Heading3"], fontName=FONT_BOLD, fontSize=13
    )
    normal_style = ParagraphStyle("NormalCustom", parent=styles["Normal"], fontName=FONT, fontSize=10)

    elements = [
        Paragraph("Envanter / Stok Takip ve Tahmin Sistemi", subtitle_style),
        Paragraph("Genel Durum Raporu", title_style),
        Paragraph(f"Oluşturulma tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}", subtitle_style),
        Spacer(1, 10),
    ]

    summary_data = [
        ["Toplam Malzeme", str(summary["total_materials"])],
        ["Kritik Malzeme", str(summary["critical_materials"])],
        ["Son 7 Günde Toplam Tüketim", f"{summary['total_consumption_7d']} ton"],
    ]
    summary_table = Table(summary_data, colWidths=[7 * cm, 7 * cm])
    summary_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (0, -1), FONT_BOLD),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e4e4e7")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 16))

    if alerts:
        alert_style = ParagraphStyle(
            "Alert", parent=styles["Normal"], fontName=FONT, fontSize=11,
            backColor=colors.HexColor("#fef2f2"), borderPadding=10,
        )
        names = ", ".join(a["name"] for a in alerts)
        elements.append(Paragraph(f"<b>⚠ Kritik seviyedeki malzemeler:</b> {names}", alert_style))
        elements.append(Spacer(1, 16))

    elements.append(Paragraph("Malzeme Listesi", heading_style))
    elements.append(Spacer(1, 6))
    material_rows = [["Malzeme", "Stok", "Kritik Eşik", "Durum"]]
    for m in materials:
        material_rows.append(
            [m["name"], f"{m['current_stock']} {m['unit']}", f"{m['critical_threshold']} {m['unit']}", m["status"].capitalize()]
        )
    material_table = Table(material_rows, colWidths=[5.5 * cm, 4 * cm, 4 * cm, 3 * cm])
    table_style = [
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f4f5f7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e4e4e7")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]
    for i, m in enumerate(materials, start=1):
        if m["status"] == "kritik":
            table_style.append(("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#dc2626")))
            table_style.append(("FONTNAME", (3, i), (3, i), FONT_BOLD))
    material_table.setStyle(TableStyle(table_style))
    elements.append(material_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Son 30 Günlük Tüketim Karşılaştırması", heading_style))
    chart_buf = build_comparison_bar_chart(comparison)
    elements.append(Image(chart_buf, width=16 * cm, height=7.4 * cm))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_material_report(analysis: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], fontName=FONT_BOLD, fontSize=18, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], fontName=FONT, textColor=colors.grey, fontSize=10, spaceAfter=6
    )
    heading_style = ParagraphStyle(
        "HeadingCustom", parent=styles["Heading3"], fontName=FONT_BOLD, fontSize=13
    )

    is_critical = analysis["current_stock"] <= analysis["critical_threshold"]
    status = "Kritik" if is_critical else "Normal"
    status_color = colors.HexColor("#dc2626") if is_critical else colors.HexColor("#16a34a")

    elements = [
        Paragraph("Envanter / Stok Takip ve Tahmin Sistemi", subtitle_style),
        Paragraph(f"Malzeme Analiz Raporu — {analysis['material_name']}", title_style),
        Paragraph(f"Oluşturulma tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}", subtitle_style),
        Spacer(1, 10),
    ]

    data = [
        ["Mevcut Stok", f"{analysis['current_stock']} {analysis['unit']}"],
        ["Kritik Eşik", f"{analysis['critical_threshold']} {analysis['unit']}"],
        ["Ortalama Günlük Tüketim", f"{analysis['avg_daily_consumption']} {analysis['unit']}/gün"],
        ["Durum", status],
    ]
    table = Table(data, colWidths=[7 * cm, 7 * cm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#3f3f46")),
                ("FONTNAME", (0, 0), (0, -1), FONT_BOLD),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e4e4e7")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (1, 3), (1, 3), status_color),
                ("FONTNAME", (1, 3), (1, 3), FONT_BOLD),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 16))

    forecast_bg = colors.HexColor("#fef2f2") if is_critical else colors.HexColor("#f0fdf4")
    forecast_style = ParagraphStyle(
        "Forecast",
        parent=styles["Normal"],
        fontName=FONT,
        fontSize=11,
        backColor=forecast_bg,
        borderPadding=10,
    )
    elements.append(Paragraph(f"<b>Tahmin:</b> {analysis['forecast_message']}", forecast_style))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Son 90 Günlük Tüketim Grafiği", heading_style))
    chart_buf = build_consumption_chart(analysis["daily_consumption"], analysis["unit"])
    elements.append(Image(chart_buf, width=16 * cm, height=6.9 * cm))

    doc.build(elements)
    buffer.seek(0)
    return buffer
