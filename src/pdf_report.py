from __future__ import annotations
from io import BytesIO
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether,
)


def _format_number(value) -> str:
    try:
        if pd.isna(value):
            return "-"
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _make_chart(data: pd.DataFrame, series_name: str, anomalies: pd.DataFrame, degree: int) -> BytesIO | None:
    """Create one production chart and return it as an in-memory PNG."""
    if series_name == "Total Production":
        values = data.drop(columns=["Date", "Total Production"], errors="ignore").apply(
            pd.to_numeric, errors="coerce"
        ).sum(axis=1, min_count=1)
    else:
        if series_name not in data.columns:
            return None
        values = pd.to_numeric(data[series_name], errors="coerce")

    valid = values.notna() & data["Date"].notna()
    if not valid.any():
        return None

    dates = data.loc[valid, "Date"]
    y = values.loc[valid].astype(float)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(dates, y, linewidth=1.6, marker="o", markersize=2.5, label="Daily production")

    if len(y) > degree:
        x = np.arange(len(y), dtype=float)
        x_center = x.mean()
        x_scale = max(float(np.ptp(x)), 1.0)
        coefficients = np.polyfit((x - x_center) / x_scale, y.to_numpy(), degree)
        trend = np.polyval(coefficients, (x - x_center) / x_scale)
        ax.plot(dates, trend, linestyle="--", linewidth=1.5, label=f"Polynomial trendline (degree {degree})")

    if not anomalies.empty and "Mine" in anomalies.columns:
        mine_anomalies = anomalies[anomalies["Mine"].astype(str).isin([series_name, "In total"] if series_name == "Total Production" else [series_name])]
        if not mine_anomalies.empty:
            for anomaly_type, marker in [("Spike", "^"), ("Drop", "v")]:
                group = mine_anomalies[mine_anomalies["Type"] == anomaly_type]
                if group.empty:
                    continue
                ax.scatter(
                    pd.to_datetime(group["Date"], errors="coerce"),
                    pd.to_numeric(group["Value"], errors="coerce"),
                    marker=marker, s=48, label=f"{anomaly_type} anomaly", zorder=4,
                )

    ax.set_title(f"Daily Production - {series_name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Production")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer


def generate_pdf_report(
    df: pd.DataFrame,
    statistics: pd.DataFrame,
    anomalies: pd.DataFrame,
    parameters: dict,
    trendline_degree: int = 1,
) -> bytes:
    """Build a PDF report with statistics, charts, anomaly details, and settings."""
    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="Mine Production Analytics Report",
        author="Mine Production Analytics",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontSize=23, leading=28, alignment=TA_LEFT, textColor=colors.HexColor("#16324F"), spaceAfter=8))
    styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading1"], fontSize=15, leading=19, textColor=colors.HexColor("#16324F"), spaceBefore=12, spaceAfter=8))
    styles.add(ParagraphStyle(name="SmallText", parent=styles["BodyText"], fontSize=8, leading=11))
    styles.add(ParagraphStyle(name="TableHeader", parent=styles["SmallText"], fontName="Helvetica-Bold", textColor=colors.HexColor("#243746")))
    styles.add(ParagraphStyle(name="AnomalyTitle", parent=styles["Heading2"], fontSize=11, leading=14, textColor=colors.HexColor("#16324F"), spaceBefore=8, spaceAfter=4))

    story = []
    dates = pd.to_datetime(df.get("Date", pd.Series(dtype="datetime64[ns]")), errors="coerce").dropna()
    date_min = dates.min().strftime("%Y-%m-%d") if not dates.empty else "N/A"
    date_max = dates.max().strftime("%Y-%m-%d") if not dates.empty else "N/A"
    mine_columns = [c for c in df.columns if c != "Date"]
    total_anomalies = len(anomalies) if anomalies is not None else 0
    spikes = int((anomalies["Type"] == "Spike").sum()) if total_anomalies and "Type" in anomalies else 0
    drops = int((anomalies["Type"] == "Drop").sum()) if total_anomalies and "Type" in anomalies else 0

    story.append(Paragraph("Mine Production Analytics Report", styles["ReportTitle"]))
    story.append(Paragraph("Daily production statistics, anomaly detection, and trend analysis", styles["BodyText"]))
    story.append(Spacer(1, 8 * mm))
    cover_rows = [
        [Paragraph("Report generated", styles["TableHeader"]), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), styles["SmallText"])],
        [Paragraph("Analysis period", styles["TableHeader"]), Paragraph(f"{date_min} to {date_max}", styles["SmallText"])],
        [Paragraph("Mines included", styles["TableHeader"]), Paragraph(str(len(mine_columns)), styles["SmallText"])],
        [Paragraph("Daily records", styles["TableHeader"]), Paragraph(str(len(df)), styles["SmallText"])],
        [Paragraph("Detected anomalies", styles["TableHeader"]), Paragraph(str(total_anomalies), styles["SmallText"])],
    ]
    cover = Table(cover_rows, colWidths=[48 * mm, 105 * mm])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#243746")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5DEE8")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.extend([cover, Spacer(1, 7 * mm)])

    story.append(Paragraph("1. Executive Summary", styles["SectionTitle"]))
    story.append(Paragraph(
        f"The report covers {len(df)} daily records from {len(mine_columns)} production series. "
        f"The configured analysis identified {total_anomalies} anomaly records: {spikes} spikes and {drops} drops. "
        "An anomaly record represents one observation flagged by one detection method; the same observation may be listed more than once when multiple methods detect it.",
        styles["BodyText"],
    ))

    story.append(Paragraph("2. Production Statistics", styles["SectionTitle"]))
    stat_frame = statistics.reset_index().copy()
    stat_frame = stat_frame.rename(columns={stat_frame.columns[0]: "Mine"})
    columns = [c for c in ["Mine", "Available Days", "Mean", "Standard Deviation", "Median", "Q1", "Q3", "IQR", "Minimum", "Maximum"] if c in stat_frame.columns]
    table_data = [[Paragraph(str(c), styles["TableHeader"]) for c in columns]]
    for _, row in stat_frame[columns].iterrows():
        table_data.append([Paragraph(str(row[c]) if c in ["Mine", "Available Days"] else _format_number(row[c]), styles["SmallText"]) for c in columns])
    stats_table = Table(table_data, repeatRows=1, hAlign="LEFT")
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.white),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#243746")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CFD8E3")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FB")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(stats_table)

    story.append(PageBreak())
    story.append(Paragraph("3. Production Charts", styles["SectionTitle"]))
    chart_data = df.copy()
    chart_data["Date"] = pd.to_datetime(chart_data["Date"], errors="coerce")
    if "Total Production" not in chart_data.columns:
        source_columns = [c for c in chart_data.columns if c != "Date"]
        chart_data["Total Production"] = chart_data[source_columns].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)
    for mine in [c for c in chart_data.columns if c not in ["Date", "Total Production"]] + ["Total Production"]:
        chart_buffer = _make_chart(chart_data, mine, anomalies if anomalies is not None else pd.DataFrame(), trendline_degree)
        if chart_buffer is not None:
            story.append(Paragraph(mine, styles["Heading2"]))
            story.append(Image(chart_buffer, width=175 * mm, height=73 * mm))
            story.append(Spacer(1, 3 * mm))

    story.append(PageBreak())
    story.append(Paragraph("4. Detected Anomalies", styles["SectionTitle"]))
    if anomalies is None or anomalies.empty:
        story.append(Paragraph("No anomalies were detected with the current parameters.", styles["BodyText"]))
    else:
        anomaly_data = anomalies.copy()
        if "Date" in anomaly_data:
            anomaly_data["Date"] = pd.to_datetime(anomaly_data["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
        visible_columns = [c for c in ["Date", "Mine", "Value", "Method", "Type", "Reference Value", "Deviation (%)", "Lower Bound", "Upper Bound", "Score", "Alpha", "Critical Value"] if c in anomaly_data.columns]
        overview_rows = [[Paragraph(str(c), styles["TableHeader"]) for c in visible_columns]]
        for _, row in anomaly_data[visible_columns].iterrows():
            overview_rows.append([Paragraph(_format_number(row[c]) if c not in ["Date", "Mine", "Method", "Type"] else str(row[c]), styles["SmallText"]) for c in visible_columns])
        overview = Table(overview_rows, repeatRows=1, hAlign="LEFT")
        overview.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.white),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#243746")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CFD8E3")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FB")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(overview)
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph("4.1 Individual Anomaly Details", styles["SectionTitle"]))
        for number, (_, row) in enumerate(anomaly_data.iterrows(), start=1):
            anomaly_type = str(row.get("Type", "Anomaly"))
            details = [
                f"Mine: {row.get('Mine', 'N/A')}",
                f"Date: {row.get('Date', 'N/A')}",
                f"Observed production: {_format_number(row.get('Value'))}",
                f"Detection method: {row.get('Method', 'N/A')}",
                f"Type: {anomaly_type}",
            ]
            for detail_col in ["Reference Value", "Deviation (%)", "Lower Bound", "Upper Bound", "Score", "Alpha", "Critical Value"]:
                if detail_col in row and pd.notna(row[detail_col]):
                    details.append(f"{detail_col}: {_format_number(row[detail_col])}")
            details.append("Interpretation: This observation was flagged by the stated statistical method and its configured parameters. The result indicates an unusual value, but does not by itself establish the cause.")
            story.append(KeepTogether([
                Paragraph(f"Anomaly #{number} - {anomaly_type}", styles["AnomalyTitle"]),
                Paragraph("<br/>".join(details), styles["SmallText"]),
                Spacer(1, 3 * mm),
            ]))

    story.append(PageBreak())
    story.append(Paragraph("5. Detection Parameters", styles["SectionTitle"]))
    if parameters:
        parameter_rows = [["Parameter", "Value"]]
        parameter_rows.extend([[str(key), str(value)] for key, value in parameters.items()])
        parameter_rows.append(["Trendline polynomial degree", str(trendline_degree)])
        parameter_table = Table(parameter_rows, colWidths=[80 * mm, 70 * mm], repeatRows=1)
        parameter_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.white),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#243746")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CFD8E3")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FB")]),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(parameter_table)
    else:
        story.append(Paragraph("Default detection parameters were used.", styles["BodyText"]))

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(16 * mm, 9 * mm, "Mine Production Analytics")
        canvas.drawRightString(landscape(A4)[0] - 16 * mm if document.pagesize == landscape(A4) else A4[0] - 16 * mm, 9 * mm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return output.getvalue()
