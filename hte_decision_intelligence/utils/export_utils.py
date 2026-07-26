import io
import pandas as pd

def generate_excel_report(title, kpis, insights_bullets, df_table):
    """
    Generates a structured Excel summary report in memory.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Executive KPI & Insights Summary
        summary_rows = [
            ["REPORT TITLE", title],
            ["", ""],
            ["KEY PERFORMANCE INDICATORS", ""],
            ["Total Enrollment", kpis.get("total_enrollment", 0)],
            ["Avg Placement Rate (%)", kpis.get("avg_placement", 0.0)],
            ["Avg Dropout Rate (%)", kpis.get("avg_dropout", 0.0)],
            ["Total Funding (Lakhs)", kpis.get("total_funding", 0.0)],
            ["Student-Faculty Ratio", kpis.get("avg_ratio", 0.0)],
            ["Total Active Institutions", kpis.get("total_institutes", 0)],
            ["", ""],
            ["AI EXECUTIVE INSIGHTS", ""]
        ]

        for bullet in insights_bullets:
            summary_rows.append(["Insight", bullet.replace("•", "").strip()])

        summary_df = pd.DataFrame(summary_rows, columns=["Category / Metric", "Value / Detail"])
        summary_df.to_excel(writer, sheet_name="Executive Summary", index=False)

        # Sheet 2: Data Records
        if not df_table.empty:
            df_table.to_excel(writer, sheet_name="Filtered Data", index=False)

    return output.getvalue()


def generate_pdf_report(title, kpis, insights_bullets, df_table):
    """
    Generates a PDF executive report using ReportLab if installed,
    or falls back to formatted summary text buffer.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0E1117"),
            spaceAfter=12
        )
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#008080"),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#222222")
        )

        story.append(Paragraph(f"HTE Decision Intelligence: {title}", title_style))
        story.append(Spacer(1, 10))

        # KPI Table
        kpi_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Enrollment", f"{kpis.get('total_enrollment', 0):,}", "Avg Placement Rate", f"{kpis.get('avg_placement', 0):.1f}%"],
            ["Avg Dropout Rate", f"{kpis.get('avg_dropout', 0):.1f}%", "Total Funding (Lakhs)", f"₹{kpis.get('total_funding', 0):,.1f}"],
            ["Student-Faculty Ratio", f"{kpis.get('avg_ratio', 0):.1f}", "Active Institutes", f"{kpis.get('total_institutes', 0)}"]
        ]
        t = Table(kpi_data, colWidths=[130, 130, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A1F2C")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F9FA")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        # Insights Section
        story.append(Paragraph("AI Executive Key Findings", heading_style))
        for bullet in insights_bullets:
            clean_b = bullet.replace("•", "").strip()
            story.append(Paragraph(f"• {clean_b}", body_style))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 15))

        # Data Snippet Table
        story.append(Paragraph("Data Overview (Top 10 Records)", heading_style))
        if not df_table.empty:
            cols = ['institute_name', 'district', 'department', 'enrollment', 'placement_pct']
            available_cols = [c for c in cols if c in df_table.columns]
            snippet = df_table[available_cols].head(10)
            
            table_data = [available_cols] + snippet.values.tolist()
            dt = Table(table_data, colWidths=[160, 90, 120, 70, 80])
            dt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#00D2C4")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ]))
            story.append(dt)

        doc.build(story)
        return buffer.getvalue()
    except Exception as e:
        # Simple plain text PDF fallback if reportlab fails
        text_report = f"HTE DECISION INTELLIGENCE REPORT\nTitle: {title}\n\nKPI SUMMARY:\n"
        for k, v in kpis.items():
            text_report += f" - {k}: {v}\n"
        text_report += "\nAI INSIGHTS:\n" + "\n".join(insights_bullets)
        return text_report.encode('utf-8')
